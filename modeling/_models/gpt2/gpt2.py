import os
from functools import cached_property

import tensorflow as tf
from tensorflow.core.protobuf import rewriter_config_pb2
from tensorflow.python.client import device_lib

from . import openai


class ModelSession:

    @staticmethod
    def create(threads=-1, server=None):
        """
            Returns a tf.Session w/ config
            """
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        config.graph_options.rewrite_options.layout_optimizer = rewriter_config_pb2.RewriterConfig.OFF
        if threads > 0:
            config.intra_op_parallelism_threads = threads
            config.inter_op_parallelism_threads = threads

        if server is not None:
            return tf.Session(target=server.target, config=config)
        return tf.Session(config=config)


class GPT2(tf.keras.Model):
    files = (
        'checkpoint',
        'encoder.json',
        'hparams.json',
        'model.ckpt.data-00000-of-00001',
        'model.ckpt.index',
        'model.ckpt.meta',
        'vocab.bpe'
    )

    def __init__(self):
        self.session = ModelSession.create()

    def finetune(
            self,
            dataset,
            steps=-1,
            model_name='124M',
            model_dir='pretrained',
            combine=50000,
            batch_size=1,
            learning_rate=0.0001,
            accumulate_gradients=5,
            restore_from='latest',
            checkpoint_path='checkpoint/run',
            sample_every=100,
            sample_length=1023,
            sample_num=1,
            multi_gpu=False,
            save_every=1000,
            print_every=1,
            max_checkpoints=1,
            use_memory_saving_gradients=False,
            only_train_transformer_layers=False,
            optimizer='adam',
            overwrite=False
    ):
        """Finetunes the model on the given dataset.

        Adapted from https://github.com/nshepperd/gpt-2/blob/finetuning/train.py.
        See that file for parameter definitions.

        assert model_name not in ['774M', '1558M'] or multi_gpu, "Currently, a modern single GPU cannot finetune the 774M GPT-2 model or larger."
        """

        pretrained_path = os.path.join(model_dir, model_name)
        self.copy_files_to_checkpoint(checkpoint_path)

        hparams = openai.model.HParams.from_file(
            filepath=os.path.join(checkpoint_path, 'hparams.json')
        )

        if sample_length > hparams.n_ctx:
            raise ValueError(f"Can't get samples longer than window size: {hparams.n_ctx}")

        # training starts
        context = tf.placeholder(tf.int32, [batch_size, None])
        output = openai.model.model(hparams=hparams, X=context, gpus=self.gpus)
        loss = tf.reduce_mean(
            input_tensor=tf.nn.sparse_softmax_cross_entropy_with_logits(
                labels=context[:, 1:],
                logits=output['logits'][:, :-1]
            )
        )

        tf_sample = openai.sample.sample_sequence(
            hparams=hparams,
            length=sample_length,
            context=context,
            batch_size=batch_size,
            temperature=1.0,
            top_k=40
        )

        # if accumulate_gradients > 1:
        opt = openai.accumulate.AccumulatingOptimizer(
            opt=self.get_optimizer(optimizer, learning_rate),
            var_list=self.train_vars(only_train_transformer_layers)
        )

        opt_reset = opt.reset()
        opt_compute = opt.compute_gradients(loss)
        opt_apply = opt.apply_gradients()
        summary_loss = tf.summary.scalar('loss', opt_apply)

        summary_log = tf.summary.FileWriter(checkpoint_path)
        saver = tf.train.Saver(var_list=self.all_vars, max_to_keep=max_checkpoints)

        self.session.run(
            tf.global_variables_initializer()
        )

        checkpoint = self.get_checkpoint_or_pretrained(checkpoint_path, pretrained_path)

        print('Loading checkpoint', checkpoint)
        saver.restore(self.session, checkpoint)

        print('Loading dataset...')
        encoder = openai.encoder.get_encoder(checkpoint_path)
        chunks = openai.load_dataset.load_dataset(encoder, dataset, combine)
        data_sampler = openai.load_dataset.Sampler(chunks)
        print('dataset has', data_sampler.total_size, 'tokens')

        print('Training...')
        counter = 1
        counter_path = os.path.join(checkpoint_path, 'counter')


    def copy_files_to_checkpoint(self, checkpoint_path, files_to_copy=('hparams.json', 'encoder.json', 'vocab.bpe')):
        # TODO
        # def maketree(path):
        #     try:
        #         os.makedirs(path)
        #     except:
        #         pass
        #
        # maketree(checkpoint_path)
        # files = [f for f in os.listdir(checkpoint_path)]
        # for file in ['hparams.json', 'encoder.json', 'vocab.bpe']:
        #     try:
        #         shutil.copyfile(os.path.join(model_dir, model_name, file),
        #                         os.path.join(checkpoint_path, file))
        #     except FileNotFoundError as fnf_error:
        #         print("You need to download the GPT-2 model first via download_gpt2()")
        #         raise (fnf_error)
        pass

    @cached_property
    def gpus(self):
        local_device_protos = device_lib.list_local_devices()
        return [x.name for x in local_device_protos if x.device_type == 'GPU']

    @property
    def all_vars(self):
        return [v for v in tf.trainable_variables() if 'model' in v.name]

    def train_vars(self, only_train_transformer_layers):
        return [v for v in self.all_vars if '/h' in v.name] if only_train_transformer_layers else self.all_vars

    def get_optimizer(self, name, lr):
        return {
            "adam": tf.train.AdamOptimizer(learning_rate=lr),
            "sgd": tf.train.GradientDescentOptimizer(learning_rate=lr),
        }.get(name)

    def get_checkpoint_or_pretrained(self, checkpoint_path, pretrained_path):
        ckpt = tf.train.latest_checkpoint(checkpoint_path)
        if ckpt is None:
            # Get fresh GPT weights if new run.
            ckpt = tf.train.latest_checkpoint(pretrained_path)
        return ckpt
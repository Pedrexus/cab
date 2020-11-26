import os

import gpt_2_simple as gpt2
import tensorflow as tf
from fuzzywuzzy import fuzz


tf.compat.v1.disable_eager_execution()


class CABModel:

    qtag = "[QUESTION]:"
    atag = "[ANSWER]:"
    impossible = "It is not possible to answer this question."

    def __init__(self, run_name: str = "test"):
        self.run_name = run_name
        self.session = gpt2.start_tf_sess()

        model_name = "124M"
        if not os.path.isdir(os.path.join("models", model_name)):
            print(f"Downloading {model_name} model...")
            gpt2.download_gpt2(model_name=model_name)

    def finetune(self, dataset, *args, **kwargs):
        gpt2.finetune(
            self.session,
            run_name=self.run_name,
            dataset=dataset,
            *args,
            **kwargs
        )
        return self

    def generate(self, prefix, *args, **kwargs):
        return gpt2.generate(
            self.session,
            self.run_name,
            prefix=prefix,
            *args,
            **kwargs
        )

    @staticmethod
    def _read_prediction(prediction, kind):
        return (line.replace(kind, '') for txt in prediction for line in txt.split('\n') if line.startswith(kind))

    def _response(self, prefix):
        prediction = self.generate(prefix, return_as_list=True)

        questions = self._read_prediction(prediction, self.qtag)
        answers = self._read_prediction(prediction, self.atag)
        return {q: a for q, a in zip(questions, answers) if a != self.impossible}

    def questions(self, context):
        prefix = f"<|startoftext|>\n[CONTEXT]: {context}\n[QUESTION]:"
        return self._response(prefix)

    def answer(self, question, context=None):
        context = f"\n[CONTEXT]: {context}" if context else ""
        prefix = f"""<|startoftext|>{context}\n[QUESTION]:{question}\n[ANSWER]:"""
        response = self._response(prefix)

        try:
            return response[question]
        except KeyError:
            # fallback to the closest question (maybe the question we asked was impossible)
            fuzzy_question = max(response, key=lambda k: fuzz.token_sort_ratio(question, k))
            return response[fuzzy_question]
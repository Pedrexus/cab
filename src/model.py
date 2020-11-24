import os

import gpt_2_simple as gpt2
import tensorflow as tf

"""
def get_abs_text(context):
    text_list = context.split('\n')
    i = 0
    for txt in text_list:
        if txt.startswith("Abstract: "):
            return text_list[i:]
        i += 1
    return text_list


def remove_citation(line):
    p = re.compile('\[\d+[, \d+]*\]')
    return p.sub('', line)


def article_to_text(article):
    txt_list = get_abs_text(article)
    context = []
    p = re.compile('\[\d+[, \d+]*\]')
    for txt in txt_list:
        context.append(p.sub('', txt))
    return '\n'.join(context)


def to_text(paragraph):
    text = ""
    c, q, a, e = "<|startoftext|>\n[CONTEXT]: ", "\n[QUESTION]:", "\n[ANSWER]:", "\n<|endoftext|>\n"
    text += c + article_to_text(paragraph['context'])
    for qas in paragraph['qas']:
        text += q + qas['question']
        if qas['is_impossible']:
            text += a + "It is not possible to answer this question."
        else:
            for answer in qas['answers']:
                text += a + answer['text']
    text += e
    return text


def dsjson_to_dstxt(json_file):
    ds = None
    with open(json_file, 'r', encoding='utf-8') as f:
        ds = json.load(f)
    dataset = ds['data']
    txt_data = ""
    for doc in dataset:
        for paragraph in doc['paragraphs']:
            txt_data += to_text(paragraph)
    return txt_data


dataset = dsjson_to_dstxt('COVID-QA.json')

with open("QAdataset.txt", "w+", encoding='utf-8') as f:
    f.write(dataset)
"""

tf.compat.v1.disable_eager_execution()

model_name = "124M"
if not os.path.isdir(os.path.join("models", model_name)):
    print(f"Downloading {model_name} model...")
    gpt2.download_gpt2(model_name=model_name)


class CABModel:

    def __init__(self):
        self.session = gpt2.start_tf_sess()

    def finetune(self, dataset):
        gpt2.finetune(
            self.session,
            dataset=dataset,
            model_dir='models',
            model_name='124M',
            steps=1000,
            restore_from='fresh',
            run_name='QA',
            print_every=1,
            sample_every=2000,
            save_every=100
        )
        return self

    def generate(self, prefix):
        return gpt2.generate(
            self.session,
            length=100,
            temperature=1,
            prefix=prefix,
            nsamples=5,
            batch_size=1,
            run_name="QA",
            return_as_list=True
        )

    def _response(self, prefix, kind):
        prediction = self.generate(prefix)
        return [line.replace(kind, '') for txt in prediction for line in txt.split('\n') if line.startswith(kind)]

    def question(self, context):
        prefix = f"<|startoftext|>\n[CONTEXT]: {context}\n[QUESTION]:"
        return self._response(prefix, kind="[QUESTION]:")

    def answer(self, question, context=None):
        context = f"\n[CONTEXT]: {context}" if context else ""
        prefix = f"""<|startoftext|>{context}\n[QUESTION]:{question}\n[ANSWER]:"""
        return self._response(prefix, kind="[QUESTION]:")
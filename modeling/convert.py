import json
import re
from tqdm import tqdm

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
    for doc in tqdm(dataset):
        for paragraph in doc['paragraphs']:
            txt_data += to_text(paragraph)
    return txt_data


dataset = dsjson_to_dstxt('squad-train-v2.0.json')

with open("SQUAD.txt", "w+", encoding='utf-8') as f:
    f.write(dataset)

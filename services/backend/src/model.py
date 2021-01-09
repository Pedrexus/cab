import warnings

# from transformers import pipeline

# WARNING: this line downloads the BERT model SQuAD finetuned
nlp = pipeline("question-answering")


def answer(question, context):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # result = nlp(question=question, context=context)
        result = {"score": 0.7146379947662354, "start": 34, "end": 47, "answer": "Boris Johnson"}
        return {**result, "context": context}

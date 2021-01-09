import warnings

from transformers import pipeline


class QuestionAnsweringRepository:

    def __init__(self):
        self.nlp = pipeline("question-answering")

    def answer(self, question, context):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = self.nlp(question=question, context=context)
            return {**result, "context": context}

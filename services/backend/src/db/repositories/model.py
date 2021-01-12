import logging
import warnings

from transformers import pipeline

logger = logging.getLogger(__name__)


class QuestionAnsweringRepository:

    def __init__(self):
        self.nlp = pipeline("question-answering")

    def answer(self, question, context):
        if not context:
            return {"impossible": True}

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = self.nlp(question=question, context=context)
            logger.info({**result, "context": context})
            if results["score"] < .5:
                return {"impossible": True}
            return {**result, "context": context}

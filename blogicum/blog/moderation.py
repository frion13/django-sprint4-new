from functools import cache

import torch
from django.conf import settings
from transformers import AutoModelForSequenceClassification, AutoTokenizer


MODEL_NAME = 'cointegrated/rubert-tiny-toxicity'


@cache
def load_moderation_model():
    """Загрузить и закешировать токенизатор и модель модерации."""
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()
    return tokenizer, model


def get_toxicity_score(text: str) -> float:
    """Вернуть оценку токсичности от 0 до 1."""
    tokenizer, model = load_moderation_model()
    inputs = tokenizer(
        text,
        return_tensors='pt',
        truncation=True,
        padding=True,
    )
    with torch.inference_mode():
        probabilities = torch.sigmoid(model(**inputs).logits)[0]
    non_toxic = probabilities[0].item()
    dangerous = probabilities[-1].item()
    return 1 - non_toxic * (1 - dangerous)


def is_toxic(text: str) -> bool:
    """Определить, достигла ли оценка заданного порога."""
    return get_toxicity_score(text) >= settings.TOXICITY_THRESHOLD

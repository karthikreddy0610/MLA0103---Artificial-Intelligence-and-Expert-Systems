# model_engine.py

import torch
from transformers import AutoTokenizer, AutoModel
import torch.nn.functional as F

MODEL_NAME = "distilbert-base-uncased"

# Load tokenizer + base transformer model (NO classification head)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

model.eval()

# Force CPU (safe for laptop)
device = torch.device("cpu")
model.to(device)


def get_embedding(text: str):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    # Mean pooling
    embedding = outputs.last_hidden_state.mean(dim=1)
    return embedding


def semantic_score(text: str):
    embedding = get_embedding(text)

    # Convert embedding to deterministic score
    score = torch.norm(embedding).item()

    # Normalize score to 0–100
    score = (score % 1) * 100

    return round(score, 2)

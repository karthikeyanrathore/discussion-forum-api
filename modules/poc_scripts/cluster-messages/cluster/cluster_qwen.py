#!/usr/bin/enn python3
import torch
import numpy as np
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from sklearn.cluster import KMeans

def message_vector(mssgs, embedding_model):
    tokenizer = AutoTokenizer.from_pretrained(embedding_model, padding_side="left")
    _model = AutoModel.from_pretrained(embedding_model)
    _model.eval()

    if isinstance(mssgs, np.ndarray):
        mssgs = mssgs.tolist()

    mssg_tokens = tokenizer(mssgs, padding=True, truncation=True, max_length=512, return_tensors="pt")

    # Forward pass
    with torch.no_grad():
        outputs = _model(**mssg_tokens)

    mssg_embeddings = last_token_pool(outputs.last_hidden_state, mssg_tokens["attention_mask"])
    mssg_embeddings = F.normalize(mssg_embeddings, p=2, dim=1)
    return mssg_embeddings 

def kmeans_msgembed(mssg_embeddings, mssgs):
    K = 4
    assert len(mssgs) >= K
    X = mssg_embeddings.cpu().to(torch.float32).numpy()
    print(X.shape)
    _kmeans_plusplus = KMeans(n_clusters = K , init='k-means++', random_state=42)
    _kmeans_plusplus.fit(X)
    batch_ids = _kmeans_plusplus.labels_
    for cluster_id in range(K):
        print(f"\n── Cluster {cluster_id} ──")
        for i, c_id in enumerate(batch_ids):
            if c_id == cluster_id:
                print(f"  {mssgs[i]}")


def last_token_pool(last_hidden_states, attention_mask):
    left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
    if left_padding:
        return last_hidden_states[:, -1]
    else:
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden_states.shape[0]
        return last_hidden_states[
            torch.arange(batch_size, device=last_hidden_states.device),
            sequence_lengths
        ]



model = "Qwen/Qwen3-Embedding-0.6B"
messages = np.array([
    "I love eating pizza on weekends.",
    "She ordered a bowl of pasta for dinner.",
    "They went to a restaurant to try Italian food.",
    "He is cooking rice and vegetables.",
    "We had coffee and cake in the afternoon.",

    "I took a train to Berlin last week.",
    "She booked a flight to Paris.",
    "They are planning a road trip across Germany.",
    "He missed the bus this morning.",
    "We rented a car for our vacation.",

    "I am learning Python programming.",
    "She fixed a bug in the software.",
    "They are building a mobile application.",
    "He bought a new laptop yesterday.",
    "We installed a new operating system.",

    "I go to the gym every day.",
    "She is practicing yoga in the morning.",
    "They are running in the park.",
    "He is trying to eat healthy food.",
    "We went for a long walk yesterday."
])
mssg_embeddings = message_vector(messages, model)
kmeans_msgembed(mssg_embeddings, messages)


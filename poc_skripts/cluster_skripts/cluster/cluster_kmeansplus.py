#!/usr/bin/env python3
import openai
from openai import OpenAI
import umap
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import os

def read_openai_keys():
    file_path = os.getenv("OPENAI_KEYS_PATH", "openai.keys")  # Default to "openai.keys" if not set
    try:
        with open(file_path, "r") as file:
            api_key = file.read().strip()
            if not api_key:
                raise ValueError("The API key file is empty.")
            return api_key
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' was not found.")
    except Exception as e:
        raise RuntimeError(f"An error occurred while reading the API key: {e}")

client = OpenAI(api_key=read_openai_keys())

def embed_messages_with_openai(messages, model="text-embedding-3-large"):
    # preprocess the messages first, before building embeddings 
    messages = [message.lower() for message in messages]
    messages = [
        message.replace("?", "").replace("!", "").replace("@", "").replace("#", "")
        for message in messages
    ]
    embeddings = []
    for message in messages:
        response = client.embeddings.create(input=message, model=model)
        embeddings.append(response.data[0].embedding)
    return np.vstack(embeddings)

def kmeans_msgembed(mssg_embeddings, mssgs):
    K = 4
    assert len(mssgs) >= K
    X= mssg_embeddings
    # X = mssg_embeddings.cpu().to(torch.float32).numpy()
    print(X.shape)
    _kmeans_plusplus = KMeans(n_clusters = K , init='k-means++', random_state=42)
    _kmeans_plusplus.fit(X)
    batch_ids = _kmeans_plusplus.labels_
    for cluster_id in range(K):
        print(f"\n── Cluster {cluster_id} ──")
        for i, c_id in enumerate(batch_ids):
            if c_id == cluster_id:
                print(f"  {mssgs[i]}")


if __name__ == "__main__":
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
    print(messages.shape)
    embeddings = embed_messages_with_openai(messages)
    # d2space_embeddings = reduce_dim_with_umap(embeddings, n_components=2, random_state=42)
    # reduced_embeddings = apply_umap_to_embeddings(embeddings, n_components=5, random_state=42)
    # labels = cluster_with_kmeans(reduced_embeddings, n_clusters=4, random_state=42)
    # (20, 3072) dim
    # print(d2space_embeddings.shape)
    kmeans_msgembed(embeddings, messages)


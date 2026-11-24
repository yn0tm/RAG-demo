from sentence_transformers import SentenceTransformer
import torch

model_name = "BAAI/bge-small-zh-v1.5"

model = SentenceTransformer(model_name)

def generate_embeddings(chunks):
    """
    将多个文本 Chunk 转换成 Embedding 向量
    """
    if not chunks:
        return []
    embeddings = model.encode(
        chunks,
        convert_to_numpy=True
    )
    return embeddings

def retrieve(query, chunks, embeddings, top_k=2):
    if top_k <= 0:
        raise ValueError("top_k 必须大于 0")

    if top_k > len(chunks):
        raise ValueError("top_k 不能超过 Chunk 数量")
    
    query_embedding = model.encode(query, convert_to_tensor=True)

    if not torch.is_tensor(embeddings):
        embeddings = torch.tensor(embeddings)

    similarities = model.similarity(
        query_embedding,
        embeddings
    ).flatten()
    topk_scores, topk_ids = torch.topk(similarities, k=top_k, dim=-1)

    topk_ids = topk_ids.tolist()
    topk_scores = topk_scores.tolist()

    return [
        {"text": chunks[i], "score": float(score)}
        for i, score in zip(topk_ids, topk_scores)
    ]
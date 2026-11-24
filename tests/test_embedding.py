from embedding import *

chunks = [
    "GPT 使用 Transformer 架构。",
    "GPT 通过预测下一个 Token 生成文本。",
    "RAG 是检索增强生成技术。"
]

embeddings = generate_embeddings(chunks)

print("Chunk 数量：", len(chunks))
print("Embedding 数量：", len(embeddings))
print("Embedding 维度：", embeddings.shape)
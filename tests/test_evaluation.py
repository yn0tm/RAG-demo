
from embedding import model
from vector_store import create_collection, retrieve_from_db
from evaluation import precision_at_k


# 1. 创建 Collection
collection = create_collection()


# 2. 输入问题
query = "Causal Mask 有什么作用？"


# 3. 生成 Query Embedding
query_embedding = model.encode(query)


# 4. 检索 Top-K
results = retrieve_from_db(
    collection,
    query_embedding,
    top_k=3
)


# 5. 人工标记相关 Chunk ID
# 这里先根据实际检索结果填写
relevant_ids = {
    "663dec176bba435ca885ea97e9ee516a_b4b379f7b7b8_0"
}


# 6. 计算 Precision@K
score = precision_at_k(
    results,
    relevant_ids,
    k=3
)


# 7. 输出结果
print("\n========== 检索评估 ==========")

for i, result in enumerate(results, start=1):
    print(f"\n排名：{i}")
    print(f"Chunk ID：{result['id']}")
    print(f"Distance：{result['distance']:.4f}")
    print(f"内容：{result['text'][:100]}")

print(f"\nPrecision@3：{score:.2f}")

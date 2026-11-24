
from embedding import model
from vector_store import create_collection, retrieve_from_db

from evaluation import (
    precision_at_k,
    recall_at_k,
    f1_at_k,
    reciprocal_rank
)

from evaluation_dataset import evaluation_dataset


def run_evaluation(top_k=3):

    collection = create_collection()

    all_results = []

    print("\n========== RAG 检索评估开始 ==========")

    for item in evaluation_dataset:

        query = item["query"]
        relevant_ids = item["relevant_ids"]

        # 1. 生成问题向量
        query_embedding = model.encode(query)

        # 2. 执行向量检索
        results = retrieve_from_db(
            collection,
            query_embedding,
            top_k=top_k
        )

        # 3. 计算评价指标
        precision = precision_at_k(
            results, relevant_ids, top_k
        )

        recall = recall_at_k(
            results, relevant_ids, top_k
        )

        f1 = f1_at_k(
            results, relevant_ids, top_k
        )

        rr = reciprocal_rank(
            results, relevant_ids, top_k
        )

        # 4. 保存本次结果
        all_results.append({
            "query": query,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "rr": rr
        })

        print(f"\n问题：{query}")
        print(f"检索数量：{len(results)}")
        print(f"Precision@{top_k}：{precision:.4f}")
        print(f"Recall@{top_k}：{recall:.4f}")
        print(f"F1@{top_k}：{f1:.4f}")
        print(f"RR@{top_k}：{rr:.4f}")

    # 5. 计算整体平均指标
    count = len(all_results)

    if count == 0:
        print("没有测试问题")
        return

    avg_precision = sum(
        x["precision"] for x in all_results
    ) / count

    avg_recall = sum(
        x["recall"] for x in all_results
    ) / count

    avg_f1 = sum(
        x["f1"] for x in all_results
    ) / count

    mrr = sum(
        x["rr"] for x in all_results
    ) / count

    print("\n========== 整体评估报告 ==========")
    print(f"测试问题数量：{count}")
    print(f"平均 Precision@{top_k}：{avg_precision:.4f}")
    print(f"平均 Recall@{top_k}：{avg_recall:.4f}")
    print(f"平均 F1@{top_k}：{avg_f1:.4f}")
    print(f"MRR@{top_k}：{mrr:.4f}")


if __name__ == "__main__":
    run_evaluation(top_k=3)

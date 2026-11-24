def precision_at_k(results, relevant_ids, k):
    """
    计算 Precision@K

    Args:
        results: 检索结果列表，每个元素包含 id
        relevant_ids: 人工标记的相关 Chunk ID 集合
        k: 评价前 K 个检索结果

    Returns:
        Precision@K 分数
    """

    if k <= 0:
        raise ValueError("k 必须大于 0")

    if not results:
        return 0.0

    # 只评价前 K 个结果
    top_k_results = results[:k]

    # 统计相关结果数量
    relevant_count = 0

    for result in top_k_results:
        if result["id"] in relevant_ids:
            relevant_count += 1

    # Precision@K 的分母始终是 K
    return relevant_count / k


def recall_at_k(results, relevant_ids, k):
    """
    计算 Recall@K

    Args:
        results: 检索结果列表
        relevant_ids: 所有人工标注的相关 Chunk ID
        k: 评价前 K 个检索结果

    Returns:
        Recall@K 分数
    """

    if k <= 0:
        raise ValueError("k 必须大于 0")

    if not relevant_ids:
        return 0.0

    top_k_results = results[:k]

    retrieved_relevant_ids = {
        result["id"]
        for result in top_k_results
        if result["id"] in relevant_ids
    }

    return len(retrieved_relevant_ids) / len(relevant_ids)


def f1_at_k(results, relevant_ids, k):
    precision = precision_at_k(results, relevant_ids, k)
    recall = recall_at_k(results, relevant_ids, k)

    if precision + recall == 0:
        return 0.0

    return 2 * precision * recall / (precision + recall)


def reciprocal_rank(results, relevant_ids, k):
    """
    计算单个问题的 Reciprocal Rank

    Args:
        results: 按相关性距离排序的检索结果
        relevant_ids: 人工标记的相关 Chunk ID
        k: 评价前 K 个结果

    Returns:
        Reciprocal Rank
    """

    if k <= 0:
        raise ValueError("k 必须大于 0")

    for rank, result in enumerate(results[:k], start=1):
        if result["id"] in relevant_ids:
            return 1 / rank

    return 0.0


def mean_reciprocal_rank(all_results, all_relevant_ids, k):
    """
    计算多个问题的 MRR

    Args:
        all_results: 多个问题各自的检索结果
        all_relevant_ids: 每个问题对应的相关 Chunk ID
        k: 评价前 K 个结果

    Returns:
        MRR@K
    """

    if len(all_results) != len(all_relevant_ids):
        raise ValueError("检索结果数量与相关 ID 集合数量必须一致")

    if not all_results:
        return 0.0

    rr_scores = []

    for results, relevant_ids in zip(all_results, all_relevant_ids):
        rr = reciprocal_rank(results, relevant_ids, k)
        rr_scores.append(rr)

    return sum(rr_scores) / len(rr_scores)

import numpy as np

def cosine_similarity(vec1, vec2):
    # 判断条件
    if l1 == 0 or l2 == 0:
        raise ValueError("零向量无法计算余弦相似度")

    # 1. 计算两个向量的点积
    dot = np.dot(vec1, vec2)
    # 2. 计算两个向量的模长
    l1 = np.linalg.norm(vec1)
    l2 = np.linalg.norm(vec2)

    # 3. 计算余弦相似度
    cos_sim = dot/(l1*l2)

    # 4. 返回结果
    return cos_sim
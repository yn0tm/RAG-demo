
# vector_store.py
# 专门负责 ChromaDB 的初始化、存储、删除和检索

import chromadb


def create_collection():
    client = chromadb.PersistentClient(path="./my_rag_db")

    collection = client.get_or_create_collection(
        name="rag_documents"
    )

    return collection


def add_document_chunks(
    collection,
    document_id,
    filename,
    file_hash,
    chunks,
    embeddings
):
    # 1. 检查数据数量是否一致
    if len(chunks) != len(embeddings):
        raise ValueError("Chunk 数量与 Embedding 数量不一致")

    if len(chunks) == 0:
        raise ValueError("不能保存空的 Chunk 列表")

    # 2. 生成带版本号的 ID
    ids = [
        f"{document_id}_{file_hash[:12]}_{i}"
        for i in range(len(chunks))
    ]

    # 3. 创建 metadata
    metadatas = [
        {
            "document_id": document_id,
            "filename": filename,
            "file_hash": file_hash,
            "chunk_index": i
        }
        for i in range(len(chunks))
    ]

    # 4. 保存到 ChromaDB
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist()
            if hasattr(embeddings, "tolist")
            else embeddings,
        metadatas=metadatas
    )

    print(f"成功保存 {len(chunks)} 个 Chunk")
    print(f"当前文档版本：{file_hash[:12]}")


def delete_old_document_versions(
    collection,
    document_id,
    current_file_hash
):
    # 查询该文档所有旧版本
    result = collection.get(
        where={"document_id": document_id},
        include=["metadatas"]
    )

    old_ids = []

    for chunk_id, metadata in zip(
        result["ids"],
        result["metadatas"]
    ):
        if metadata["file_hash"] != current_file_hash:
            old_ids.append(chunk_id)

    # 删除旧版本
    if old_ids:
        collection.delete(ids=old_ids)
        print(f"已删除 {len(old_ids)} 个旧版本 Chunk")
    else:
        print("没有需要删除的旧版本")


def inspect_document_chunks(collection, document_id):

    result = collection.get(
        where={"document_id": document_id},
        include=["documents", "metadatas"]
    )

    print(f"当前文档 Chunk 数量：{len(result['ids'])}")

    for chunk_id, document, metadata in zip(
        result["ids"],
        result["documents"],
        result["metadatas"]
    ):
        print("----------------------------")
        print("Chunk ID:", chunk_id)
        print("Chunk 内容:", document)
        print("Metadata:", metadata)


def retrieve_from_db(collection, query_embedding, top_k=3, distance_threshold=None):

    if top_k <= 0:
        raise ValueError("top_k 必须大于 0")

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    # 整理查询结果
    formatted_results = []

    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for chunk_id, document, metadata, distance in zip(
        ids, documents, metadatas, distances
    ):
        # 距离阈值过滤
        if (
            distance_threshold is not None
            and distance > distance_threshold
        ):
            continue
        formatted_results.append({
            "id": chunk_id,
            "text": document,
            "metadata": metadata,
            "distance": distance
        })

    return formatted_results
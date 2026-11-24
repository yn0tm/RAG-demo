import hashlib
from pathlib import Path

from document_loader import load_document
from document_registry import (
    register_document,
    update_document_status,
    mark_document_ready
)

from text_splitter import split_text
from embedding import generate_embeddings

from vector_store import (
    create_collection,
    add_document_chunks,
    delete_old_document_versions
)


def calculate_file_hash(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def process_document(file_path):

    # 1. 读取文档
    text = load_document(file_path)

    if text is None:
        print("文档读取失败，终止处理")
        return

    if not text.strip():
        print("文档内容为空，终止处理")
        return

    # 2. 计算文件 Hash
    file_hash = calculate_file_hash(file_path)

    # 3. 获取文件名
    filename = Path(file_path).name

    # 4. 注册文档
    result = register_document(filename, file_hash)

    document_id = result["document_id"]
    action = result["action"]

    if action == "unchanged":
        print("文档内容没有变化，无需重新处理")
        return

    elif action == "duplicate":
        print("发现重复文档，终止处理")
        return

    elif action not in ("new", "updated", "retry"):
        print(f"未知操作类型：{action}")
        return

    print(f"文档需要处理，document_id: {document_id}")
    print(f"当前操作类型：{action}")

    try:
        # 5. 文本切分
        chunks = split_text(
            text,
            chunk_size=500,
            chunk_overlap=50
        )

        if not chunks:
            raise ValueError("文本切分失败，没有生成 Chunk")

        print(f"成功生成 {len(chunks)} 个 Chunk")

        # 6. 生成 Embedding
        embeddings = generate_embeddings(chunks)

        if len(embeddings) != len(chunks):
            raise ValueError("Embedding 数量与 Chunk 数量不一致")

        print(f"Embedding Shape: {embeddings.shape}")

        # 7. 初始化 ChromaDB
        collection = create_collection()

        # 8. 保存新版本
        add_document_chunks(
            collection=collection,
            document_id=document_id,
            filename=filename,
            file_hash=file_hash,
            chunks=chunks,
            embeddings=embeddings
        )

        # 9. 删除旧版本
        delete_old_document_versions(
            collection=collection,
            document_id=document_id,
            current_file_hash=file_hash
        )

        # 10. 更新 SQLite 状态
        mark_document_ready(
            document_id,
            file_hash,
            len(chunks)
        )

        print("文档处理成功！")
        print(f"Document ID: {document_id}")
        print(f"Chunk 数量: {len(chunks)}")

    except Exception as e:
        print(f"文档处理失败：{e}")
        update_document_status(document_id, "failed")
        return


if __name__ == "__main__":

    file_path = (
        r"D:\DeepLearningDemo\RAG-Demo"
        r"\data\transformer_notes.txt"
    )

    process_document(file_path)

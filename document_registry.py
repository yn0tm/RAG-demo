#专门负责 SQLite 数据库操作

import sqlite3
import uuid
from pathlib import Path
from datetime import datetime

# 1. 数据库路径
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "document_registry.db"

# 2. 初始化数据库
def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            document_id TEXT PRIMARY KEY,
            filename TEXT NOT NULL UNIQUE,
            file_hash TEXT NOT NULL UNIQUE,
            chunk_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at TEXT,
            updated_at TEXT
        )
    """
    )

    conn.commit()
    conn.close()

# 3. 根据 Hash 查询
def find_document_by_hash(file_hash):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM documents WHERE file_hash = ?",
        (file_hash,)
    )

    result = cursor.fetchone()
    conn.close()
    return result

# 4. 根据文件名查询
def find_document_by_filename(filename):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM documents WHERE filename = ?",
        (filename,)
    )

    result = cursor.fetchone()
    conn.close()
    return result

# 5. 注册新文档 INSERT
def insert_document(filename, file_hash):
    #1.生成文档ID
    document_id = uuid.uuid4().hex

    #2.获取当前时间
    now = datetime.now().isoformat()

    #3.连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    #4.插入数据
    cursor.execute(
        """
        INSERT INTO documents (
            document_id,
            filename,
            file_hash,
            chunk_count,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            document_id,
            filename,
            file_hash,
            0,
            "pending",
            now,
            now
        )
    )
    #5.保存并关闭
    conn.commit()
    conn.close()
    print("新文档注册成功")

    return document_id

# 6. 更新已有文档 UPDATE
def update_document(document_id, new_file_hash, new_chunk_count):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updated_at = datetime.now().isoformat(timespec="seconds")

    cursor.execute(
        """
        UPDATE documents
        SET file_hash = ?,
            chunk_count = ?,
            updated_at = ?
        WHERE document_id = ?
        """,
        (new_file_hash, new_chunk_count, updated_at, document_id)
    )
    if cursor.rowcount > 0:
        print("文档更新成功")
    else:
        print("未找到对应文档")

    conn.commit()
    conn.close()

# 7. 更新状态函数
def update_document_status(document_id, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updated_at = datetime.now().isoformat()

    cursor.execute(
        """
        UPDATE documents
        SET status = ?,
            updated_at = ?
        WHERE document_id = ?
        """,
        (status, updated_at, document_id)
    )

    conn.commit()
    conn.close()

# 8. 自动判断执行操作


def register_document(filename, file_hash):

    # 1. 根据文件名查询
    result = find_document_by_filename(filename)

    if result:

        document_id = result[0]
        old_hash = result[2]
        status = result[4]

        # 2. Hash 相同
        if old_hash == file_hash:

            if status == "ready":
                print("内容没有变化")

                return {
                    "document_id": document_id,
                    "action": "unchanged"
                }

            else:
                print("文档尚未完成处理，需要重新处理")

                return {
                    "document_id": document_id,
                    "action": "retry"
                }

        # 3. Hash 不同
        else:

            update_document_status(
                document_id,
                "pending"
            )

            print("检测到文档内容发生变化")

            return {
                "document_id": document_id,
                "action": "updated"
            }

    # 4. 文件名不存在，检查内容是否重复
    hash_result = find_document_by_hash(file_hash)

    if hash_result:

        print("内容重复")

        return {
            "document_id": None,
            "action": "duplicate"
        }

    # 5. 注册新文档
    document_id = insert_document(
        filename,
        file_hash
    )

    return {
        "document_id": document_id,
        "action": "new"
    }


# 9. 入库成功后的更新函数
def mark_document_ready(
    document_id,
    new_file_hash,
    chunk_count
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updated_at = datetime.now().isoformat()

    cursor.execute(
        """
        UPDATE documents
        SET file_hash = ?,
            chunk_count = ?,
            status = ?,
            updated_at = ?
        WHERE document_id = ?
        """,
        (new_file_hash, chunk_count, "ready", updated_at, document_id)
    )

    conn.commit()
    conn.close()
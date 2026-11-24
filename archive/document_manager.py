import hashlib

def get_file_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda:f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

#创建 Document Registry 数据表
#第一步：导入库
import sqlite3
from pathlib import Path

#第二步：确定数据库路径
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "document_registry.db"

#第三步：创建数据库和数据表
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

#实现 Hash 查询函数
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
"""
result = find_document_by_hash(file_hash)
if result:
    print("文档已存在")

else:
    print("文档不存在")
"""
#实现 文件名 查询函数
def find_document_by_filename(filename):
    #建立连接
    conn = sqlite3.connect(DB_PATH)
    #建立游标
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM documents WHERE filename = ?",
        (filename,)
    )

    result = cursor.fetchone()
    conn.close()
    return result

# 实现文档登记 INSERT
import uuid
from datetime import datetime

def register_document(filename, file_hash):

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
            "ready",
            now,
            now
        )
    )

    #5.保存并关闭
    conn.commit()
    conn.close()

#更新数据库里面的参数
def update_document(
    document_id,
    new_file_hash,
    new_chunk_count
):
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
        (
            new_file_hash, new_chunk_count, updated_at, document_id
        )
    )
    if cursor.rowcount > 0:
        print("文档更新成功")
    else:
        print("未找到对应文档")
    conn.commit()
    conn.close()

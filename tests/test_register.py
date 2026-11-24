from document_registry import (
    find_document_by_filename
)

result = find_document_by_filename(
    "transformer_notes.txt"
)

if result:
    print("========== 数据库记录 ==========")
    print("Document ID:", result[0])
    print("Filename:", result[1])
    print("File Hash:", result[2])
    print("Chunk Count:", result[3])
    print("Status:", result[4])
    print("Created At:", result[5])
    print("Updated At:", result[6])
else:
    print("数据库中没有找到该文档")
#实现文本切分
def split_text(text, chunk_size, chunk_overlap):
    if not isinstance(text, str):
        raise TypeError("text 必须是字符串")
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size 必须是正整数")
    if not isinstance(chunk_overlap, int) or chunk_overlap < 0:
        raise ValueError("chunk_overlap 必须是非负整数")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap 必须小于 chunk_size")
    
    if len(text) == 0:
        return []
    
    chunk_list = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk_list.append(text[start:end])   # 切片会自动截断到末尾
        if end >= len(text):
            break
        start = end - chunk_overlap
    return chunk_list
#读取指定文件，将文件内容提取出来，交给后续模块。
def load_document(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"文件不存在: {file_path}")
        return None
    except IsADirectoryError:
        print(f"这是一个文件夹: {file_path}")
        return None
    except PermissionError:
        print(f"没有读取权限: {file_path}")
        return None
    except UnicodeDecodeError:
        print(f"编码不是 UTF-8: {file_path}")
        return None
    return text
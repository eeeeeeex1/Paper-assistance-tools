# backend/utils/file_utils.py
def read_file_content(file):
    """读取上传文件的内容"""
    try:
        # 检查文件类型
        filename = file.filename.lower()
        if filename.endswith('.txt'):
            # 文本文件直接读取
            return file.read().decode('utf-8', errors='replace')
        elif filename.endswith(('.doc', '.docx')):
            # Word文件需要额外处理（示例中简化处理）
            # 实际项目中应使用python-docx等库
            return f"[Word文件内容: {file.filename}，此处为演示，实际项目需要解析文档内容]"
        elif filename.endswith('.pdf'):
            # PDF文件需要额外处理
            return f"[PDF文件内容: {file.filename}，此处为演示，实际项目需要使用PDF解析库]"
        else:
            return f"[未知文件类型: {file.filename}]"
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None
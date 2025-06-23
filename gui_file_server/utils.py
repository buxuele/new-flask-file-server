"""
GUI文件服务器工具函数
"""

import os
import stat
import mimetypes
from pathlib import Path
from datetime import datetime
import hashlib

def get_file_type(file_path):
    """根据文件路径获取文件类型"""
    from config import FILE_TYPES
    
    if file_path.is_dir():
        return 'folder'
    
    ext = file_path.suffix.lower().lstrip('.')
    
    for file_type, config in FILE_TYPES.items():
        if ext in config['extensions']:
            return file_type
    
    return 'file'

def get_file_icon(file_type):
    """获取文件类型对应的图标"""
    from config import FILE_TYPES
    
    return FILE_TYPES.get(file_type, {}).get('icon', '📄')

def get_file_color(file_type):
    """获取文件类型对应的颜色"""
    from config import FILE_TYPES
    
    return FILE_TYPES.get(file_type, {}).get('color', '#000000')

def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def format_timestamp(timestamp):
    """格式化时间戳"""
    dt = datetime.fromtimestamp(timestamp)
    now = datetime.now()
    
    # 如果是今天
    if dt.date() == now.date():
        return f"今天 {dt.strftime('%H:%M')}"
    
    # 如果是昨天
    elif (now - dt).days == 1:
        return f"昨天 {dt.strftime('%H:%M')}"
    
    # 如果是本年
    elif dt.year == now.year:
        return dt.strftime('%m-%d %H:%M')
    
    # 其他情况
    else:
        return dt.strftime('%Y-%m-%d %H:%M')

def get_file_permissions(file_path):
    """获取文件权限字符串"""
    try:
        st = file_path.stat()
        return stat.filemode(st.st_mode)
    except:
        return "未知"

def is_hidden_file(file_path):
    """判断是否为隐藏文件"""
    from config import HIDDEN_FILES_PATTERN
    
    name = file_path.name
    
    # 检查是否匹配隐藏文件模式
    for pattern in HIDDEN_FILES_PATTERN:
        if name.startswith(pattern):
            return True
    
    # Windows系统检查隐藏属性
    if os.name == 'nt':
        try:
            attrs = os.stat(file_path).st_file_attributes
            return attrs & stat.FILE_ATTRIBUTE_HIDDEN
        except:
            pass
    
    return False

def get_file_hash(file_path, algorithm='md5'):
    """计算文件哈希值"""
    hash_func = hashlib.new(algorithm)
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except:
        return None

def safe_path_join(base_path, *paths):
    """安全的路径拼接，防止目录穿越"""
    result = Path(base_path)
    
    for path in paths:
        # 移除可能的目录穿越字符
        clean_path = str(path).replace('..', '').replace('/', '').replace('\\', '')
        result = result / clean_path
    
    return result

def get_mime_type(file_path):
    """获取文件MIME类型"""
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type or 'application/octet-stream'

def is_text_file(file_path):
    """判断是否为文本文件"""
    mime_type = get_mime_type(file_path)
    return mime_type.startswith('text/') if mime_type else False

def is_image_file(file_path):
    """判断是否为图片文件"""
    return get_file_type(file_path) == 'image'

def is_video_file(file_path):
    """判断是否为视频文件"""
    return get_file_type(file_path) == 'video'

def is_audio_file(file_path):
    """判断是否为音频文件"""
    return get_file_type(file_path) == 'audio'

def create_thumbnail_cache_key(file_path):
    """创建缩略图缓存键"""
    stat_info = file_path.stat()
    key_string = f"{file_path}_{stat_info.st_mtime}_{stat_info.st_size}"
    return hashlib.md5(key_string.encode()).hexdigest()

def ensure_cache_dir():
    """确保缓存目录存在"""
    from config import CACHE_DIR
    
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR

def clean_cache_dir():
    """清理缓存目录"""
    from config import CACHE_DIR, THUMBNAIL_CACHE_SIZE
    
    if not CACHE_DIR.exists():
        return
    
    # 获取所有缓存文件，按修改时间排序
    cache_files = list(CACHE_DIR.glob('*'))
    cache_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    # 删除超出限制的缓存文件
    for file_path in cache_files[THUMBNAIL_CACHE_SIZE:]:
        try:
            file_path.unlink()
        except:
            pass
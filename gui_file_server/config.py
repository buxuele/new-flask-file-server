"""
GUI文件服务器配置文件
"""

import os
from pathlib import Path

# 应用配置
APP_NAME = "GUI文件浏览器"
APP_VERSION = "1.0.0"

# 默认设置
DEFAULT_ROOT_PATH = Path.home()  # 默认根目录为用户主目录
WINDOW_SIZE = "1200x800"  # 默认窗口大小
MAX_IMAGE_PREVIEWS = 50  # 最大图片预览数量
THUMBNAIL_SIZE = (150, 150)  # 缩略图大小

# 文件类型配置
FILE_TYPES = {
    'image': {
        'extensions': ['gif', 'ico', 'jpeg', 'jpg', 'png', 'svg', 'webp', 'bmp', 'tiff'],
        'icon': '🖼️',
        'color': '#4CAF50'
    },
    'video': {
        'extensions': ['mp4', 'm4v', 'ogv', 'webm', 'mov', 'avi', 'mkv', 'flv', 'wmv'],
        'icon': '🎬',
        'color': '#FF5722'
    },
    'audio': {
        'extensions': ['mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac', 'wma'],
        'icon': '🎵',
        'color': '#9C27B0'
    },
    'archive': {
        'extensions': ['7z', 'zip', 'rar', 'gz', 'tar', 'bz2', 'xz', 'lzma'],
        'icon': '📦',
        'color': '#795548'
    },
    'text': {
        'extensions': ['txt', 'md', 'py', 'js', 'css', 'html', 'json', 'yaml', 'yml', 
                      'c', 'cpp', 'java', 'php', 'rb', 'go', 'rs', 'swift'],
        'icon': '📄',
        'color': '#2196F3'
    },
    'pdf': {
        'extensions': ['pdf'],
        'icon': '📕',
        'color': '#F44336'
    },
    'office': {
        'extensions': ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'odt', 'ods', 'odp'],
        'icon': '📊',
        'color': '#FF9800'
    },
    'folder': {
        'extensions': [],
        'icon': '📁',
        'color': '#FFC107'
    },
    'executable': {
        'extensions': ['exe', 'msi', 'deb', 'rpm', 'dmg', 'app'],
        'icon': '⚙️',
        'color': '#607D8B'
    }
}

# 界面主题配置
THEMES = {
    'default': {
        'bg_color': '#ffffff',
        'fg_color': '#000000',
        'select_color': '#0078d4',
        'accent_color': '#106ebe'
    },
    'dark': {
        'bg_color': '#2d2d2d',
        'fg_color': '#ffffff',
        'select_color': '#404040',
        'accent_color': '#0078d4'
    }
}

# 快捷键配置
SHORTCUTS = {
    'refresh': '<F5>',
    'go_up': '<Alt-Up>',
    'go_home': '<Ctrl-h>',
    'new_folder': '<Ctrl-Shift-n>',
    'delete': '<Delete>',
    'rename': '<F2>',
    'properties': '<Alt-Return>'
}

# 安全配置
HIDDEN_FILES_PATTERN = ['.', '__pycache__', '.git', '.svn', 'Thumbs.db', '.DS_Store']
MAX_FILE_SIZE_MB = 1000  # 最大文件大小限制（MB）

# 缓存配置
CACHE_DIR = Path.home() / '.gui_file_server_cache'
THUMBNAIL_CACHE_SIZE = 100  # 缩略图缓存数量
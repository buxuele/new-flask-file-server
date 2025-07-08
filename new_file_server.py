import os
import mimetypes
import humanize
import stat
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, make_response, request, send_file, Response
from flask.views import MethodView
from werkzeug.utils import secure_filename

# --- 配置区 ---
# 设置文件服务的根目录，'.' 表示当前目录，您也可以设置为绝对路径如 'F:\\'

# 设置一个安全的密钥，用于未来的认证功能
SECRET_KEY = "your-very-secret-key"
# --- 结束配置 ---


app = Flask(__name__)
app.secret_key = SECRET_KEY

# 定义不同文件类型，用于前端判断
DATATYPES = {
    'image': ['gif', 'ico', 'jpeg', 'jpg', 'png', 'svg', 'webp'],
    'video': ['mp4', 'm4v', 'ogv', 'webm', 'mov'],
    'audio': ['mp3', 'wav', 'ogg', 'm4a'],
    'archive': ['7z', 'zip', 'rar', 'gz', 'tar'],
    'text': ['py', 'js', 'css', 'html', 'json', 'yaml', 'c', 'cpp', 'java'],
    'ebook': ['epub', 'mobi', 'azw3', 'pdf', "txt", "md"],
}

# 定义文件图标
ICONS = {
    'image': 'bi-image',
    'video': 'bi-film',
    'audio': 'bi-music-note-beamed',
    'archive': 'bi-archive-fill',
    'text': 'bi-file-earmark-text',
    'pdf': 'bi-file-earmark-pdf',
    'folder': 'bi-folder-fill',
    'file': 'bi-file-earmark',  # 默认文件图标
    # --- 新增开始 ---
    'ebook': 'bi-book-half',  # 为电子书选一个图标
    # --- 新增结束 ---
}


def get_file_type_and_icon(filename_str):
    """根据文件名后缀返回文件类型和对应的 Bootstrap 图标"""
    ext = filename_str.split('.')[-1].lower()
    for file_type, extensions in DATATYPES.items():
        if ext in extensions:
            return file_type, ICONS.get(file_type, ICONS['file'])
    return 'file', ICONS['file']


@app.template_filter('human_size')
def human_size_filter(size_bytes):
    return humanize.naturalsize(size_bytes)


@app.template_filter('human_time')
def human_time_filter(timestamp):
    return humanize.naturaltime(datetime.fromtimestamp(timestamp))


class FileServerView(MethodView):
    def get(self, p=''):
        # 防止目录穿越漏洞
        request_path = Path(os.path.normpath(p))
        if '..' in request_path.parts:
            return "禁止访问", 403

        # 构建安全的文件/目录路径
        abs_path = FILE_ROOT.joinpath(request_path)

        if not abs_path.exists():
            return "文件或目录未找到", 404

        # 处理目录浏览
        if abs_path.is_dir():
            items = []
            images = []
            total_size, file_count, dir_count = 0, 0, 0

            for item in sorted(abs_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                # 隐藏点开头的文件/目录
                if item.name.startswith('.'):
                    continue

                try:
                    stat_res = item.stat()
                except FileNotFoundError:
                    continue  # 忽略损坏的符号链接等

                entry = {
                    'name': item.name,
                    'mtime': stat_res.st_mtime,
                    'size': stat_res.st_size,
                    'is_dir': item.is_dir()
                }

                if item.is_dir():
                    entry['type'] = 'folder'
                    entry['icon'] = ICONS['folder']
                    dir_count += 1
                    items.append(entry)
                else:
                    file_type, icon_class = get_file_type_and_icon(item.name)
                    entry['type'] = file_type
                    entry['icon'] = icon_class
                    file_count += 1
                    total_size += stat_res.st_size
                    # 分离图片和其他文件
                    if file_type == 'image':
                        images.append(entry)
                    else:
                        items.append(entry)

            return render_template(
                'index.html',
                current_path=str(request_path),
                path_parts=request_path.parts,
                items=items,
                images=images,
                total_size=total_size,
                file_count=file_count,
                dir_count=dir_count
            )

        # 处理文件下载
        elif abs_path.is_file():
            # --- 修改开始 ---
            # 检查 URL 查询参数中是否有 'dl=1'
            should_download = request.args.get('dl') == '1'
            # 如果 should_download 为 True，则强制浏览器下载文件
            return send_file(abs_path, as_attachment=should_download)
            # --- 修改结束 ---

        return "无效的路径", 400

    def post(self, p=''):
        # 文件上传逻辑
        request_path = Path(os.path.normpath(p))
        if '..' in request_path.parts:
            return "禁止访问", 403

        upload_path = FILE_ROOT.joinpath(request_path)
        if not upload_path.is_dir():
            return "目标路径不是一个有效的目录", 400

        files = request.files.getlist('files[]')
        if not files:
            return "没有选择文件", 400

        for file in files:
            if file.filename:
                # 使用 secure_filename 防止恶意文件名
                filename = secure_filename(file.filename)
                try:
                    file.save(upload_path / filename)
                except Exception as e:
                    return f"保存文件 {filename} 时出错: {e}", 500

        return "上传成功", 200


# 注册视图
file_server_view = FileServerView.as_view('file_server_view')
app.add_url_rule('/', view_func=file_server_view)
app.add_url_rule('/<path:p>', view_func=file_server_view)

if __name__ == '__main__':
    # 确保根目录存在
    FILE_ROOT = Path('F:/').resolve()

    if not FILE_ROOT.exists():
        print(f"警告：根目录 '{FILE_ROOT}' 不存在。将为您创建它。")
        FILE_ROOT.mkdir(parents=True, exist_ok=True)

    # 打印访问地址
    print(f"文件服务已启动，根目录为: {FILE_ROOT}")
    print("请在浏览器中访问以下地址之一:")

    # 在生产环境中，推荐使用 Gunicorn 或其他 WSGI 服务器
    # gunicorn -w 4 -b 0.0.0.0:5050 file_server_bs5:app
    app.run(host='0.0.0.0', port=5050, debug=True)

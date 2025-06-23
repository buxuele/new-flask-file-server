#!/usr/bin/env python3
"""
GUI File Server - Desktop version of the Flask file server
Based on the original Flask web application
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import stat
import mimetypes
import humanize
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageTk
import threading
import webbrowser

class FileServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("文件浏览器 - GUI版本")
        self.root.geometry("1200x800")
        
        # 当前路径
        self.current_path = Path.home()  # 默认从用户主目录开始
        
        # 文件类型定义
        self.DATATYPES = {
            'image': ['gif', 'ico', 'jpeg', 'jpg', 'png', 'svg', 'webp', 'bmp'],
            'video': ['mp4', 'm4v', 'ogv', 'webm', 'mov', 'avi', 'mkv'],
            'audio': ['mp3', 'wav', 'ogg', 'm4a', 'flac'],
            'archive': ['7z', 'zip', 'rar', 'gz', 'tar', 'bz2'],
            'text': ['txt', 'md', 'py', 'js', 'css', 'html', 'json', 'yaml', 'c', 'cpp', 'java'],
            'pdf': ['pdf'],
        }
        
        # 创建界面
        self.create_widgets()
        self.refresh_view()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顶部工具栏
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 路径显示和导航
        path_frame = ttk.Frame(toolbar_frame)
        path_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(path_frame, text="当前路径:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, state='readonly')
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 按钮框架
        button_frame = ttk.Frame(toolbar_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="🏠 主目录", command=self.go_home).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="⬆️ 上级目录", command=self.go_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🔄 刷新", command=self.refresh_view).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="📁 选择目录", command=self.select_directory).pack(side=tk.LEFT, padx=(0, 5))
        
        # 右侧按钮
        ttk.Button(button_frame, text="📤 上传文件", command=self.upload_files).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="📂 新建文件夹", command=self.create_folder).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 创建笔记本控件用于分页显示
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 文件列表页面
        self.create_file_list_tab()
        
        # 图片预览页面
        self.create_image_preview_tab()
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
        
    def create_file_list_tab(self):
        # 文件列表框架
        list_frame = ttk.Frame(self.notebook)
        self.notebook.add(list_frame, text="📋 文件列表")
        
        # 创建Treeview
        columns = ('名称', '类型', '大小', '修改时间')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='tree headings')
        
        # 设置列标题
        self.tree.heading('#0', text='图标')
        for col in columns:
            self.tree.heading(col, text=col)
            
        # 设置列宽
        self.tree.column('#0', width=50)
        self.tree.column('名称', width=300)
        self.tree.column('类型', width=100)
        self.tree.column('大小', width=100)
        self.tree.column('修改时间', width=150)
        
        # 滚动条
        scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', self.on_item_double_click)
        
        # 右键菜单
        self.create_context_menu()
        
    def create_image_preview_tab(self):
        # 图片预览框架
        preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(preview_frame, text="🖼️ 图片预览")
        
        # 创建滚动画布
        canvas = tk.Canvas(preview_frame)
        scrollbar_v = ttk.Scrollbar(preview_frame, orient="vertical", command=canvas.yview)
        scrollbar_h = ttk.Scrollbar(preview_frame, orient="horizontal", command=canvas.xview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_v.pack(side="right", fill="y")
        scrollbar_h.pack(side="bottom", fill="x")
        
        self.image_canvas = canvas
        
    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="打开", command=self.open_selected)
        self.context_menu.add_command(label="删除", command=self.delete_selected)
        self.context_menu.add_command(label="重命名", command=self.rename_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="属性", command=self.show_properties)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        
    def show_context_menu(self, event):
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            self.context_menu.post(event.x_root, event.y_root)
            
    def get_file_type_and_icon(self, filename):
        """根据文件名后缀返回文件类型"""
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        for file_type, extensions in self.DATATYPES.items():
            if ext in extensions:
                return file_type
        return 'file'
        
    def get_file_icon(self, file_type, is_dir=False):
        """返回文件类型对应的图标字符"""
        if is_dir:
            return "📁"
        
        icons = {
            'image': '🖼️',
            'video': '🎬',
            'audio': '🎵',
            'archive': '📦',
            'text': '📄',
            'pdf': '📕',
            'file': '📄'
        }
        return icons.get(file_type, '📄')
        
    def refresh_view(self):
        """刷新当前目录视图"""
        try:
            # 更新路径显示
            self.path_var.set(str(self.current_path))
            
            # 清空树形视图
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # 清空图片预览
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
                
            if not self.current_path.exists():
                self.status_var.set("路径不存在")
                return
                
            items = []
            images = []
            total_size = 0
            file_count = 0
            dir_count = 0
            
            # 遍历目录内容
            for item in sorted(self.current_path.iterdir(), 
                             key=lambda x: (not x.is_dir(), x.name.lower())):
                if item.name.startswith('.'):
                    continue
                    
                try:
                    stat_info = item.stat()
                    mtime = datetime.fromtimestamp(stat_info.st_mtime)
                    
                    if item.is_dir():
                        # 目录
                        icon = self.get_file_icon('folder', True)
                        self.tree.insert('', 'end', text=icon, values=(
                            item.name, '文件夹', '', mtime.strftime('%Y-%m-%d %H:%M:%S')
                        ))
                        dir_count += 1
                    else:
                        # 文件
                        file_type = self.get_file_type_and_icon(item.name)
                        icon = self.get_file_icon(file_type)
                        size_str = humanize.naturalsize(stat_info.st_size)
                        
                        self.tree.insert('', 'end', text=icon, values=(
                            item.name, file_type, size_str, mtime.strftime('%Y-%m-%d %H:%M:%S')
                        ))
                        
                        file_count += 1
                        total_size += stat_info.st_size
                        
                        # 如果是图片，添加到图片预览
                        if file_type == 'image':
                            images.append(item)
                            
                except (OSError, PermissionError):
                    continue
                    
            # 更新状态栏
            self.status_var.set(f"{dir_count} 个文件夹, {file_count} 个文件, "
                              f"总大小 {humanize.naturalsize(total_size)}")
            
            # 加载图片预览
            self.load_image_previews(images)
            
        except PermissionError:
            messagebox.showerror("错误", "没有权限访问此目录")
        except Exception as e:
            messagebox.showerror("错误", f"刷新目录时出错: {str(e)}")
            
    def load_image_previews(self, image_files):
        """加载图片预览"""
        def load_images():
            row = 0
            col = 0
            max_cols = 4
            
            for img_path in image_files[:20]:  # 限制显示前20张图片
                try:
                    # 创建缩略图
                    with Image.open(img_path) as img:
                        img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        
                        # 创建图片框架
                        img_frame = ttk.Frame(self.scrollable_frame)
                        img_frame.grid(row=row, column=col, padx=5, pady=5)
                        
                        # 图片标签
                        img_label = ttk.Label(img_frame, image=photo)
                        img_label.image = photo  # 保持引用
                        img_label.pack()
                        
                        # 文件名标签
                        name_label = ttk.Label(img_frame, text=img_path.name, 
                                             wraplength=150, justify=tk.CENTER)
                        name_label.pack()
                        
                        # 绑定点击事件
                        img_label.bind("<Button-1>", 
                                     lambda e, path=img_path: self.open_file(path))
                        
                        col += 1
                        if col >= max_cols:
                            col = 0
                            row += 1
                            
                except Exception as e:
                    print(f"加载图片 {img_path} 失败: {e}")
                    continue
                    
        # 在后台线程中加载图片
        threading.Thread(target=load_images, daemon=True).start()
        
    def on_item_double_click(self, event):
        """处理双击事件"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        filename = self.tree.item(item, 'values')[0]
        file_path = self.current_path / filename
        
        if file_path.is_dir():
            self.current_path = file_path
            self.refresh_view()
        else:
            self.open_file(file_path)
            
    def open_file(self, file_path):
        """打开文件"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{file_path}"' if os.uname().sysname == 'Darwin' 
                         else f'xdg-open "{file_path}"')
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件: {str(e)}")
            
    def go_home(self):
        """回到主目录"""
        self.current_path = Path.home()
        self.refresh_view()
        
    def go_up(self):
        """上级目录"""
        if self.current_path.parent != self.current_path:
            self.current_path = self.current_path.parent
            self.refresh_view()
            
    def select_directory(self):
        """选择目录"""
        directory = filedialog.askdirectory(initialdir=self.current_path)
        if directory:
            self.current_path = Path(directory)
            self.refresh_view()
            
    def upload_files(self):
        """上传文件"""
        files = filedialog.askopenfilenames(
            title="选择要上传的文件",
            initialdir=self.current_path
        )
        
        if files:
            success_count = 0
            for file_path in files:
                try:
                    src = Path(file_path)
                    dst = self.current_path / src.name
                    
                    if dst.exists():
                        if not messagebox.askyesno("文件已存在", 
                                                 f"文件 {src.name} 已存在，是否覆盖？"):
                            continue
                            
                    shutil.copy2(src, dst)
                    success_count += 1
                    
                except Exception as e:
                    messagebox.showerror("错误", f"复制文件 {src.name} 失败: {str(e)}")
                    
            if success_count > 0:
                messagebox.showinfo("成功", f"成功复制 {success_count} 个文件")
                self.refresh_view()
                
    def create_folder(self):
        """新建文件夹"""
        folder_name = tk.simpledialog.askstring("新建文件夹", "请输入文件夹名称:")
        if folder_name:
            try:
                new_folder = self.current_path / folder_name
                new_folder.mkdir(exist_ok=False)
                messagebox.showinfo("成功", f"文件夹 '{folder_name}' 创建成功")
                self.refresh_view()
            except FileExistsError:
                messagebox.showerror("错误", "文件夹已存在")
            except Exception as e:
                messagebox.showerror("错误", f"创建文件夹失败: {str(e)}")
                
    def open_selected(self):
        """打开选中的文件/文件夹"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            filename = self.tree.item(item, 'values')[0]
            file_path = self.current_path / filename
            
            if file_path.is_dir():
                self.current_path = file_path
                self.refresh_view()
            else:
                self.open_file(file_path)
                
    def delete_selected(self):
        """删除选中的文件/文件夹"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        filename = self.tree.item(item, 'values')[0]
        file_path = self.current_path / filename
        
        if messagebox.askyesno("确认删除", f"确定要删除 '{filename}' 吗？"):
            try:
                if file_path.is_dir():
                    shutil.rmtree(file_path)
                else:
                    file_path.unlink()
                messagebox.showinfo("成功", f"'{filename}' 已删除")
                self.refresh_view()
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {str(e)}")
                
    def rename_selected(self):
        """重命名选中的文件/文件夹"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        old_name = self.tree.item(item, 'values')[0]
        new_name = tk.simpledialog.askstring("重命名", "请输入新名称:", initialvalue=old_name)
        
        if new_name and new_name != old_name:
            try:
                old_path = self.current_path / old_name
                new_path = self.current_path / new_name
                old_path.rename(new_path)
                messagebox.showinfo("成功", f"已重命名为 '{new_name}'")
                self.refresh_view()
            except Exception as e:
                messagebox.showerror("错误", f"重命名失败: {str(e)}")
                
    def show_properties(self):
        """显示文件/文件夹属性"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        filename = self.tree.item(item, 'values')[0]
        file_path = self.current_path / filename
        
        try:
            stat_info = file_path.stat()
            
            # 创建属性窗口
            prop_window = tk.Toplevel(self.root)
            prop_window.title(f"属性 - {filename}")
            prop_window.geometry("400x300")
            
            # 属性信息
            info_text = tk.Text(prop_window, wrap=tk.WORD, padx=10, pady=10)
            info_text.pack(fill=tk.BOTH, expand=True)
            
            info = f"""文件名: {filename}
路径: {file_path}
类型: {'文件夹' if file_path.is_dir() else '文件'}
大小: {humanize.naturalsize(stat_info.st_size)}
创建时间: {datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}
修改时间: {datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
访问时间: {datetime.fromtimestamp(stat_info.st_atime).strftime('%Y-%m-%d %H:%M:%S')}
权限: {stat.filemode(stat_info.st_mode)}
"""
            
            info_text.insert(tk.END, info)
            info_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("错误", f"获取属性失败: {str(e)}")


def main():
    root = tk.Tk()
    
    # 导入必要的模块
    try:
        import tkinter.simpledialog
        tk.simpledialog = tkinter.simpledialog
    except ImportError:
        pass
    
    app = FileServerGUI(root)
    
    # 设置窗口图标（如果有的话）
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    root.mainloop()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
GUI文件服务器启动器
提供更友好的启动界面和错误处理
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

def check_dependencies():
    """检查必要的依赖"""
    missing_deps = []
    
    try:
        import PIL
    except ImportError:
        missing_deps.append("Pillow")
    
    try:
        import humanize
    except ImportError:
        missing_deps.append("humanize")
    
    return missing_deps

def install_dependencies(deps):
    """安装缺失的依赖"""
    import subprocess
    
    for dep in deps:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        except subprocess.CalledProcessError:
            return False
    return True

def main():
    # 创建启动窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 检查依赖
    missing_deps = check_dependencies()
    
    if missing_deps:
        result = messagebox.askyesno(
            "缺少依赖",
            f"检测到缺少以下依赖包:\n{', '.join(missing_deps)}\n\n是否自动安装？"
        )
        
        if result:
            messagebox.showinfo("安装中", "正在安装依赖包，请稍候...")
            if install_dependencies(missing_deps):
                messagebox.showinfo("成功", "依赖包安装完成！")
            else:
                messagebox.showerror("错误", "依赖包安装失败，请手动安装")
                root.destroy()
                return
        else:
            messagebox.showwarning("警告", "没有必要的依赖包，程序可能无法正常运行")
    
    root.destroy()
    
    # 启动主程序
    try:
        from main import main as run_main
        run_main()
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("启动失败", f"程序启动失败:\n{str(e)}")
        root.destroy()

if __name__ == "__main__":
    main()
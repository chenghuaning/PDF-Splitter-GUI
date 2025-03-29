import os
from cx_Freeze import setup, Executable

# 打包配置
build_options = {
    'packages': ['tkinter', 'PyPDF2'],
    'excludes': [],
    'include_files': []
}

# 主程序配置
exe = Executable(
    script='pdf_splitter_gui.py',
    base='Win32GUI' if os.name == 'nt' else None,
    icon=None,
    target_name='PDFSplitterGUI'
)

setup(
    name='PDFSplitterGUI',
    version='1.2',
    description='PDF分割工具(GUI版)',
    options={'build_exe': build_options},
    executables=[exe]
)
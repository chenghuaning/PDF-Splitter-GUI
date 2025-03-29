# PDF分割工具 (GUI版)

一个简单易用的PDF分割工具，支持多种分割模式。

## 主要功能
- 单页分割：每页保存为单独PDF
- 按页码范围分割：提取指定页（如`1-3,5,7-9`）
- 固定页数分组：按固定页数自动分组
- 自定义分组：支持复杂分组（如`1-10,11-20,...`）

## 使用方法
### 直接运行EXE
1. 从[发布页面](https://github.com/chenghuaning/PDF-Splitter-GUI/releases)下载`PDFSplitterGUI.zip`
2. 双击PDFSplitterGUI.exe即可运行

### 从源码运行
```bash
# 克隆仓库
git clone https://github.com/chenghuaning/PDF-Splitter-GUI.git
cd PDF-Splitter-GUI

# 安装依赖
pip install -r requirements.txt

# 运行程序
python src/pdf_splitter_gui.py
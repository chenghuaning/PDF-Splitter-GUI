import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PyPDF2 import PdfReader, PdfWriter


def get_default_output_path(input_path):
    """根据输入文件路径返回同目录下的output文件夹"""
    if not input_path:
        return os.path.join(os.path.expanduser("~"), "Desktop", "output")

    input_dir = os.path.dirname(input_path)
    return os.path.join(input_dir, "output")
class PDFSplitterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF分割工具 (增强版)")
        self.root.geometry("600x500")

        # 变量初始化
        self.input_path = tk.StringVar()
        self.output_folder = tk.StringVar(value=get_default_output_path(None))
        self.mode = tk.StringVar(value="single")
        self.page_ranges = tk.StringVar()
        self.group_size = tk.IntVar(value=10)
        self.custom_groups = tk.StringVar()

        self.create_widgets()


    def create_widgets(self):
        # 输入文件选择
        ttk.Label(self.root, text="输入PDF文件:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.input_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="浏览...", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)

        # 输出文件夹选择
        ttk.Label(self.root, text="输出文件夹:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.output_folder, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="浏览...", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)

        # 分割模式选择
        ttk.Label(self.root, text="分割模式:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        mode_frame = ttk.Frame(self.root)
        mode_frame.grid(row=2, column=1, columnspan=2, sticky="w")

        modes = [
            ("单页分割", "single"),
            ("页码范围", "range"),
            ("固定分组", "group"),
            ("自定义分组", "custom")
        ]

        for text, value in modes:
            ttk.Radiobutton(
                mode_frame, text=text, variable=self.mode, value=value,
                command=self.toggle_mode_options
            ).pack(side="left", padx=5)

        # 页码范围输入
        self.range_frame = ttk.LabelFrame(self.root, text="页码范围设置")
        self.range_frame.grid(row=3, column=0, columnspan=3, sticky="we", padx=5, pady=5)
        ttk.Label(self.range_frame, text="输入页码范围 (如: 1-3,5,7-9):").pack(side="left")
        ttk.Entry(self.range_frame, textvariable=self.page_ranges, width=50).pack(side="left", padx=5)

        # 固定分组设置
        self.group_frame = ttk.LabelFrame(self.root, text="固定分组设置")
        self.group_frame.grid(row=4, column=0, columnspan=3, sticky="we", padx=5, pady=5)
        ttk.Label(self.group_frame, text="每组页数:").pack(side="left")
        ttk.Spinbox(self.group_frame, from_=1, to=1000, textvariable=self.group_size, width=5).pack(side="left", padx=5)

        # 自定义分组设置
        self.custom_frame = ttk.LabelFrame(self.root, text="自定义分组设置")
        self.custom_frame.grid(row=5, column=0, columnspan=3, sticky="we", padx=5, pady=5)
        ttk.Label(self.custom_frame, text="输入分组范围 (如: 0-9,10-20,21-30):").pack(side="left")
        ttk.Entry(self.custom_frame, textvariable=self.custom_groups, width=50).pack(side="left", padx=5)

        # 示例按钮
        ttk.Button(
            self.custom_frame, text="示例",
            command=lambda: self.custom_groups.set(
                "0-9,10-20,21-30,31-40,41-50")
        ).pack(side="left", padx=5)

        # 状态信息
        self.status_var = tk.StringVar(value="准备就绪")
        ttk.Label(self.root, textvariable=self.status_var).grid(row=6, column=0, columnspan=3, pady=10)

        # 进度条
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=550, mode="determinate")
        self.progress.grid(row=7, column=0, columnspan=3, pady=5)

        # 执行按钮
        ttk.Button(self.root, text="开始分割", command=self.execute_split).grid(row=8, column=1, pady=10)

        # 初始显示正确的选项
        self.toggle_mode_options()

    def toggle_mode_options(self):
        """根据选择的模式显示/隐藏对应选项"""
        mode = self.mode.get()
        self.range_frame.grid_remove()
        self.group_frame.grid_remove()
        self.custom_frame.grid_remove()

        if mode == "range":
            self.range_frame.grid()
        elif mode == "group":
            self.group_frame.grid()
        elif mode == "custom":
            self.custom_frame.grid()

    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        if filename:
            self.input_path.set(filename)
            # 自动设置输出文件夹为输入文件所在目录
            self.output_folder.set(get_default_output_path(filename))

    def browse_output(self):
        foldername = filedialog.askdirectory(
            title="选择输出文件夹"
        )
        if foldername:
            self.output_folder.set(foldername)

    def parse_page_ranges(self, range_str, max_page):
        """解析页码范围字符串"""
        pages = set()
        parts = [p.strip() for p in range_str.split(',') if p.strip()]

        for part in parts:
            if '-' in part:
                start, end = map(int, part.split('-'))
                pages.update(range(start, end + 1))
            else:
                pages.add(int(part))

        return sorted(p for p in pages if 1 <= p <= max_page)

    def parse_custom_groups(self, group_str, max_page):
        """解析自定义分组字符串"""
        groups = []
        parts = [p.strip() for p in group_str.split(',') if p.strip()]

        for part in parts:
            if '-' in part:
                start, end = map(int, part.split('-'))
                # 确保页码不小于1
                start = max(1, start)
                end = max(1, end)
                if start > end:
                    start, end = end, start  # 自动纠正反向范围
                groups.append((start, end))
            else:
                page = max(1, int(part))  # 确保页码不小于1
                groups.append((page, page))

        # 验证分组是否有效
        valid_groups = []
        for start, end in groups:
            if start <= end <= max_page:
                valid_groups.append((start, end))
            elif start <= max_page:  # 部分范围有效
                valid_groups.append((start, min(end, max_page)))

        return valid_groups

    def execute_split(self):
        # 验证输入
        if not self.input_path.get():
            messagebox.showerror("错误", "请选择输入PDF文件")
            return

        if not os.path.exists(self.input_path.get()):
            messagebox.showerror("错误", "输入的PDF文件不存在")
            return

        try:
            # 准备参数
            mode = self.mode.get()

            # 创建输出目录
            os.makedirs(self.output_folder.get(), exist_ok=True)

            # 读取PDF
            self.status_var.set("正在读取PDF...")
            self.root.update()

            reader = PdfReader(self.input_path.get())
            total_pages = len(reader.pages)
            filename = os.path.splitext(os.path.basename(self.input_path.get()))[0]

            # 执行分割
            if mode == "single":
                self.progress["maximum"] = total_pages
                for i in range(total_pages):
                    writer = PdfWriter()
                    writer.add_page(reader.pages[i])
                    output_path = os.path.join(
                        self.output_folder.get(),
                        f"{filename}_page{i + 1}.pdf"
                    )
                    with open(output_path, "wb") as out_file:
                        writer.write(out_file)

                    self.progress["value"] = i + 1
                    self.status_var.set(f"正在处理: 第 {i + 1}/{total_pages} 页")
                    self.root.update()

                messagebox.showinfo("完成", f"已分割为 {total_pages} 个单页PDF")

            elif mode == "range":
                ranges = self.page_ranges.get().strip()
                if not ranges:
                    messagebox.showerror("错误", "请输入页码范围")
                    return

                selected_pages = self.parse_page_ranges(ranges, total_pages)
                if not selected_pages:
                    messagebox.showerror("错误", "无效的页码范围")
                    return

                writer = PdfWriter()
                self.progress["maximum"] = len(selected_pages)

                for i, page_num in enumerate(selected_pages, 1):
                    writer.add_page(reader.pages[page_num - 1])
                    self.progress["value"] = i
                    self.status_var.set(f"正在处理: 第 {i}/{len(selected_pages)} 页")
                    self.root.update()

                output_path = os.path.join(
                    self.output_folder.get(),
                    f"{filename}_selected_pages.pdf"
                )
                with open(output_path, "wb") as out_file:
                    writer.write(out_file)

                messagebox.showinfo("完成", f"已提取 {len(selected_pages)} 页")

            elif mode == "group":
                group_size = max(1, self.group_size.get())
                group_count = (total_pages + group_size - 1) // group_size
                self.progress["maximum"] = group_count

                for g in range(group_count):
                    start = g * group_size
                    end = min(start + group_size, total_pages)

                    writer = PdfWriter()
                    for i in range(start, end):
                        writer.add_page(reader.pages[i])

                    output_path = os.path.join(
                        self.output_folder.get(),
                        f"{filename}_part{g + 1}_pages{start + 1}-{end}.pdf"
                    )
                    with open(output_path, "wb") as out_file:
                        writer.write(out_file)

                    self.progress["value"] = g + 1
                    self.status_var.set(f"正在处理: 第 {g + 1}/{group_count} 组")
                    self.root.update()

                messagebox.showinfo("完成", f"已分割为 {group_count} 个PDF文件，每组最多 {group_size} 页")


            elif mode == "custom":

                groups_str = self.custom_groups.get().strip()

                if not groups_str:
                    messagebox.showerror("错误", "请输入自定义分组范围")

                    return

                try:

                    groups = self.parse_custom_groups(groups_str, total_pages)

                    if not groups:
                        messagebox.showerror("错误", "无效的分组范围")

                        return

                    self.progress["maximum"] = len(groups)

                    for i, (start, end) in enumerate(groups, 1):

                        writer = PdfWriter()

                        # 注意: PDF页码是0-based的，所以需要start-1

                        for page_num in range(start - 1, end):  # 修改这里

                            writer.add_page(reader.pages[page_num])

                        output_path = os.path.join(

                            self.output_folder.get(),

                            # 文件名显示实际页码(1-based)

                            f"{filename}_group{i}_pages{start}-{end}.pdf"

                        )

                        with open(output_path, "wb") as out_file:

                            writer.write(out_file)

                        self.progress["value"] = i

                        self.status_var.set(f"正在处理: 第 {i}/{len(groups)} 组 ({start}-{end})")

                        self.root.update()

                    messagebox.showinfo("完成", f"已分割为 {len(groups)} 个自定义分组PDF")


                except ValueError as e:

                    messagebox.showerror("错误", f"分组格式错误: {str(e)}")

                    return

            # 重置状态
            self.status_var.set("处理完成")
            self.progress["value"] = 0

        except Exception as e:
            messagebox.showerror("错误", f"处理过程中发生错误:\n{str(e)}")
            self.status_var.set("处理失败")
        finally:
            self.root.update()


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFSplitterGUI(root)
    root.mainloop()
#!/usr/bin/env python3
"""
PDF拆分脚本
将大型PDF文件拆分成单页PDF文件，便于批量OCR处理
"""

from pypdf import PdfReader, PdfWriter
import os


def split_pdf(input_pdf_path: str, output_dir: str = "pages") -> int:
    """
    将PDF文件拆分成单页文件

    Args:
        input_pdf_path: 输入的PDF文件路径
        output_dir: 输出目录

    Returns:
        拆分的页数
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 读取PDF
    print(f"正在读取PDF文件: {input_pdf_path}")
    reader = PdfReader(input_pdf_path)
    total_pages = len(reader.pages)

    print(f"总页数: {total_pages}")
    print(f"开始拆分...")

    # 逐页拆分
    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)

        # 文件名格式: page_001.pdf, page_002.pdf, ...
        output_path = os.path.join(output_dir, f"page_{i+1:03d}.pdf")

        with open(output_path, "wb") as f:
            writer.write(f)

        # 显示进度
        if (i + 1) % 50 == 0 or (i + 1) == total_pages:
            print(f"进度: {i+1}/{total_pages} ({(i+1)/total_pages*100:.1f}%)")

    print(f"✅ 拆分完成! 共 {total_pages} 页")
    print(f"📁 输出目录: {output_dir}")

    return total_pages


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python split_pdf.py <PDF文件路径> [输出目录]")
        print("示例: python split_pdf.py '区域经济学 马工程.pdf' pages")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "pages"

    if not os.path.exists(input_pdf):
        print(f"❌ 错误: 文件不存在: {input_pdf}")
        sys.exit(1)

    split_pdf(input_pdf, output_dir)

#!/usr/bin/env python3
"""
OCR结果合并脚本
将分散的OCR文本文件合并成一个完整文件
"""

import os


def merge_ocr_results(input_dir: str, output_file: str = "final_ocr_result.txt"):
    """
    合并OCR结果

    Args:
        input_dir: OCR文本文件所在目录
        output_file: 输出文件路径
    """
    # 获取所有txt文件并排序
    txt_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".txt")])

    if not txt_files:
        print(f"❌ 错误: 在 {input_dir} 中没有找到文本文件")
        return

    print(f"📚 找到 {len(txt_files)} 个文本文件")
    print(f"🔄 开始合并...")

    all_text = []

    for idx, txt_file in enumerate(txt_files, start=1):
        txt_path = os.path.join(input_dir, txt_file)

        with open(txt_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 添加分隔符
        all_text.append(f"\n{'='*60}\n")
        all_text.append(f"📄 文件: {txt_file}\n")
        all_text.append(f"{'='*60}\n")
        all_text.append(content)

        # 显示进度
        if idx % 50 == 0 or idx == len(txt_files):
            print(f"进度: {idx}/{len(txt_files)} ({idx/len(txt_files)*100:.1f}%)")

    # 写入最终文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(all_text)

    print(f"✅ 合并完成!")
    print(f"📁 输出文件: {output_file}")
    print(f"📊 总页数: {len(txt_files)}")


def merge_ocr_results_clean(input_dir: str, output_file: str = "final_ocr_result_clean.txt"):
    """
    合并OCR结果（纯净版，不加分隔符）

    Args:
        input_dir: OCR文本文件所在目录
        output_file: 输出文件路径
    """
    txt_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".txt")])

    if not txt_files:
        print(f"❌ 错误: 在 {input_dir} 中没有找到文本文件")
        return

    print(f"📚 找到 {len(txt_files)} 个文本文件")
    print(f"🔄 开始合并（纯净版）...")

    all_text = []

    for txt_file in txt_files:
        txt_path = os.path.join(input_dir, txt_file)

        with open(txt_path, "r", encoding="utf-8") as f:
            content = f.read()

        all_text.append(content)
        all_text.append("\n\n")  # 页面之间空两行

    # 写入最终文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(all_text)

    print(f"✅ 合并完成!")
    print(f"📁 输出文件: {output_file}")
    print(f"📊 总页数: {len(txt_files)}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python merge_ocr_results.py <OCR文本目录> [输出文件名]")
        print("\n模式:")
        print("  默认模式: python merge_ocr_results.py ocr_text")
        print("           带分隔符的完整版")
        print("  纯净模式: python merge_ocr_results.py ocr_text --clean")
        print("           不加分隔符，仅保留文本内容")
        sys.exit(1)

    input_dir = sys.argv[1]

    if not os.path.exists(input_dir):
        print(f"❌ 错误: 目录不存在: {input_dir}")
        sys.exit(1)

    # 检查是否使用纯净模式
    if len(sys.argv) > 2 and sys.argv[2] == "--clean":
        merge_ocr_results_clean(input_dir)
    else:
        merge_ocr_results(input_dir)

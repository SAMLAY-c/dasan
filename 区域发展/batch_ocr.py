#!/usr/bin/env python3
"""
批量OCR脚本
支持断点续传、失败重试、日志记录
"""

import os
import time
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class OCRProcessor:
    def __init__(self):
        self.api_url = "https://api.ocr.space/parse/image"
        self.api_key = os.getenv("OCR_API_KEY")
        self.language = os.getenv("OCR_LANGUAGE", "chs")
        self.engine = os.getenv("OCR_ENGINE", "2")
        self.scale = os.getenv("OCR_SCALE", "true")
        self.timeout = int(os.getenv("REQUEST_TIMEOUT", "120"))
        self.sleep_time = float(os.getenv("SLEEP_TIME", "1.2"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))

        # 创建输出目录
        self.output_dir = "ocr_text"
        os.makedirs(self.output_dir, exist_ok=True)

        # 日志文件
        self.log_file = "ocr.log"

    def log(self, message: str):
        """写入日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")

    def ocr_single_pdf(self, pdf_path: str) -> dict:
        """
        对单个PDF文件进行OCR识别

        Args:
            pdf_path: PDF文件路径

        Returns:
            OCR结果字典
        """
        filename = os.path.basename(pdf_path)

        with open(pdf_path, "rb") as f:
            response = requests.post(
                self.api_url,
                files={"file": (filename, f, "application/pdf")},
                data={
                    "apikey": self.api_key,
                    "language": self.language,
                    "OCREngine": self.engine,
                    "scale": self.scale
                },
                timeout=self.timeout
            )

        # 确保返回的是字典
        try:
            return response.json()
        except:
            return {"error": "Invalid JSON response", "text": response.text}

    def process_single_file(self, pdf_path: str, txt_path: str) -> bool:
        """
        处理单个文件（含重试机制）

        Args:
            pdf_path: PDF文件路径
            txt_path: 输出文本文件路径

        Returns:
            是否成功
        """
        filename = os.path.basename(pdf_path)

        # 如果已经处理过，跳过
        if os.path.exists(txt_path):
            self.log(f"⏭️  跳过已处理: {filename}")
            return True

        # 重试机制
        for retry in range(self.max_retries):
            try:
                self.log(f"📄 [{retry+1}/{self.max_retries}] OCR处理: {filename}")

                result = self.ocr_single_pdf(pdf_path)

                # 检查结果
                if isinstance(result, dict) and result.get("OCRExitCode") == 1:
                    text = result["ParsedResults"][0]["ParsedText"]

                    # 保存结果
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(text)

                    self.log(f"✅ 成功: {filename}")
                    return True
                else:
                    # 处理错误响应
                    if isinstance(result, dict):
                        error_msg = result.get("ErrorMessage", result.get("error", "未知错误"))
                    else:
                        error_msg = f"API返回格式错误: {type(result)}"

                    self.log(f"❌ 失败: {filename} - {error_msg}")

                    if retry < self.max_retries - 1:
                        wait_time = (retry + 1) * 2  # 递增等待时间
                        self.log(f"⏳ 等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)

            except requests.exceptions.Timeout:
                self.log(f"⏱️  超时: {filename}")
                if retry < self.max_retries - 1:
                    time.sleep(5)
            except Exception as e:
                self.log(f"⚠️  异常: {filename} - {str(e)}")
                if retry < self.max_retries - 1:
                    time.sleep(5)

        self.log(f"💥 最终失败: {filename}")
        return False

    def batch_process(self, pdf_dir: str):
        """
        批量处理PDF文件

        Args:
            pdf_dir: PDF文件所在目录
        """
        # 获取所有PDF文件并排序
        pdf_files = sorted([f for f in os.listdir(pdf_dir) if f.endswith(".pdf")])

        if not pdf_files:
            self.log(f"❌ 错误: 在 {pdf_dir} 中没有找到PDF文件")
            return

        total = len(pdf_files)
        self.log(f"📚 开始批量OCR处理, 共 {total} 个文件")
        self.log(f"=" * 50)

        success_count = 0
        failed_count = 0

        for idx, pdf_file in enumerate(pdf_files, start=1):
            pdf_path = os.path.join(pdf_dir, pdf_file)
            txt_path = os.path.join(self.output_dir, f"{pdf_file}.txt")

            self.log(f"📍 进度: [{idx}/{total}]")

            success = self.process_single_file(pdf_path, txt_path)

            if success:
                success_count += 1
            else:
                failed_count += 1

            # 防止限流
            if idx < total:
                time.sleep(self.sleep_time)

        # 统计结果
        self.log(f"=" * 50)
        self.log(f"📊 处理完成!")
        self.log(f"   ✅ 成功: {success_count}/{total}")
        self.log(f"   ❌ 失败: {failed_count}/{total}")
        self.log(f"📁 结果保存在: {self.output_dir}/")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python batch_ocr.py <PDF文件目录>")
        print("示例: python batch_ocr.py pages")
        print("\n⚠️  请确保在.env文件中设置了OCR_API_KEY")
        sys.exit(1)

    pdf_dir = sys.argv[1]

    if not os.path.exists(pdf_dir):
        print(f"❌ 错误: 目录不存在: {pdf_dir}")
        sys.exit(1)

    # 检查API密钥
    api_key = os.getenv("OCR_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("❌ 错误: 请先在.env文件中设置OCR_API_KEY")
        print("   1. 复制 .env.example 为 .env")
        print("   2. 在 https://ocr.space/registration/ 注册获取API密钥")
        print("   3. 将密钥填入 .env 文件")
        sys.exit(1)

    processor = OCRProcessor()
    processor.batch_process(pdf_dir)

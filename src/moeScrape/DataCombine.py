import pandas as pd
import sqlite3
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import json
from .utils import TextExtractor


class DataConsolidator:
    def __init__(self, raw_data_dir="/data/policies"):
        self.raw_data_dir = Path(raw_data_dir)
        self.output_dir = Path("data/consolidated")
        self.output_dir.mkdir(exist_ok=True)

        # 初始化数据库
        self.conn = sqlite3.connect(self.output_dir / "file_index.db")
        self._init_db()

    def _init_db(self):
        """创建文件索引表"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
                doc_hash TEXT PRIMARY KEY,
                title TEXT,
                source_url TEXT,
                attachment_count INTEGER
            )
        """)

    def process_all(self):
        """主处理流程"""
        # 收集所有文档路径
        meta_files = list(self.raw_data_dir.glob("**/meta.json"))

        # 多进程处理
        with ProcessPoolExecutor() as executor:
            results = list(executor.map(self._process_single, meta_files))

        # 构建DataFrame
        df = pd.DataFrame([r for r in results if r])
        df.to_parquet(self.output_dir / "consolidated_data.parquet")

    def _process_single(self, meta_path):
        """处理单个文档"""
        try:
            with open(meta_path) as f:
                data = json.load(f)

            # 基础信息
            record = {
                "doc_hash": data['metadata']['doc_hash'],
                "title": data['content']['文件标题'],
                "main_content": data['content']['正文内容'],
                "attachments_text": ""
            }

            # 处理附件
            if data['content'].get('附件'):
                attachment_texts = []
                for att in data['content']['附件']:
                    if att['download_status'] == 'success':
                        content = self._read_attachment(att['local_path'])
                        attachment_texts.append(content)

                record['attachments_text'] = "\n---\n".join(attachment_texts)

            # 更新索引
            self.conn.execute("""
                INSERT OR REPLACE INTO files 
                VALUES (?, ?, ?, ?)
            """, (
                record['doc_hash'],
                record['title'],
                data['metadata']['source_url'],
                len(data['content'].get('附件', []))
            ))

            return record
        except Exception as e:
            print(f"处理失败：{meta_path} - {str(e)}")
            return None

    def _read_attachment(self, rel_path):
        """读取并解析附件"""
        full_path = self.raw_data_dir / rel_path
        content = full_path.read_bytes()

        if full_path.suffix.lower() == '.pdf':
            return TextExtractor.parse_pdf(content)
        elif full_path.suffix.lower() == '.docx':
            return TextExtractor.parse_docx(content)
        else:
            return ""  # 其他格式暂不处理


def task_two():
    # 初始化处理器
    processor = DataConsolidator(raw_data_dir="data/policies")

    # 执行整合（启用4进程）
    processor.process_all()

    # 结果示例
    df = pd.read_parquet("data/consolidated/consolidated_data.parquet")
    print(df.head())


if __name__ == '__main__':
    task_two()
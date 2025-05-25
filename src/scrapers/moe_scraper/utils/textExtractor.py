import os
import json
import pdfplumber
from docx import Document


def extract_pdf_text(path):
    with pdfplumber.open(path) as pdf:
        return " ".join([page.extract_text() for page in pdf.pages])


def extract_docx_text(path):
    doc = Document(path)
    return " ".join([para.text for para in doc.paragraphs])


# 遍历所有JSON文件
for json_file in os.listdir("json_folder"):
    with open(f"json_folder/{json_file}", "r") as f:
        data = json.load(f)

    # 提取附件内容
    attachment_texts = []
    for attachment in data.get("attachments", []):
        if attachment.endswith(".pdf"):
            text = extract_pdf_text(attachment)
        elif attachment.endswith(".docx"):
            text = extract_docx_text(attachment)
        attachment_texts.append(text)

    # 合并到JSON数据
    data["attachment_content"] = " ".join(attachment_texts)
    # 保存处理后的JSON（可选）
    with open(f"processed/{json_file}", "w") as f:
        json.dump(data, f)
import csv
import os
import configparser # 确保 python-docx 已安装
import docx # 确保 python-docx 已安装
from openai import OpenAI # 确保 openai 库已安装
import json # 用于解析模型输出 和 meta.json
import re

# 尝试导入 PDF 读取所需的库
try:
    import PyPDF2
except ImportError:
    print("警告: PyPDF2 库未安装。PDF文件将无法被读取。请运行 'pip3 install PyPDF2' 安装它。")
    PyPDF2 = None

# --- 配置 OpenAI 客户端 ---
def get_llm_client():
    # 创建 ConfigParser 对象
    config = configparser.ConfigParser()
    # 获取当前脚本所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'config.ini')

    # 读取配置文件
    if os.path.exists(config_path):
        config.read(config_path)
        api_key = config.get('DEFAULT', 'DASHSCOPE_API_KEY', fallback=None)
    else:
        api_key = None # 如果配置文件不存在，则 api_key 为 None

    # api_key = os.getenv("DASHSCOPE_API_KEY") # 旧的获取方式，可以注释或删除
    if not api_key:
        print("警告: 未在 config.ini 文件中找到 DASHSCOPE_API_KEY，或配置文件不存在。请确保 API Key 已正确配置。")
        # 您可以在这里决定是退出程序还是使用备用方案
        # exit() 或者 raise ValueError("API Key 未配置")

    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    return client

client = get_llm_client()

def read_questions_from_csv(csv_filepath):
    questions_data = []
    try:
        with open(csv_filepath, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                questions_data.append(row)
    except FileNotFoundError:
        print(f"错误: CSV文件未找到 {csv_filepath}")
    except Exception as e:
        print(f"读取CSV文件时发生错误: {e}")
    return questions_data

def read_docx_file(docx_filepath):
    text_content = ""
    try:
        if not os.path.exists(docx_filepath):
            print(f"错误: DOCX文件未找到 {docx_filepath}")
            return "文件未找到"
        doc = docx.Document(docx_filepath)
        for para in doc.paragraphs:
            text_content += para.text + "\n"
    except ImportError:
        print("错误: python-docx 库未安装或导入失败。请运行 'pip3 install python-docx' 来安装它。")
        return "python-docx 库未安装"
    except Exception as e:
        if "BadZipFile" in str(e) or "File is not a zip file" in str(e):
            print(f"提示: 文件 {docx_filepath} 可能不是一个有效的 DOCX 文件或已损坏。跳过此文件。")
            return "无效的DOCX文件"
        print(f"读取DOCX文件 {docx_filepath} 时发生错误: {e}")
        return f"读取文件出错: {e}"
    if not text_content.strip():
        print(f"提示: DOCX文件 {docx_filepath} 未能提取到文本，或者文件为空。")
        return "未能提取到文本或文件为空"
    return text_content

def read_pdf_file(pdf_filepath):
    text_content = ""
    if not PyPDF2:
        print(f"提示: PyPDF2 库不可用，无法读取PDF文件 {pdf_filepath}")
        return "PyPDF2库不可用"
    try:
        if not os.path.exists(pdf_filepath):
            print(f"错误: PDF文件未找到 {pdf_filepath}")
            return "文件未找到"
        with open(pdf_filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if reader.is_encrypted:
                try:
                    reader.decrypt('') # 尝试用空密码解密
                except Exception as decrypt_error:
                    print(f"提示: PDF文件 {pdf_filepath} 已加密且无法解密。跳过此文件。错误: {decrypt_error}")
                    return "加密PDF无法解密"
            
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text_content += page.extract_text() + "\n"
    except PyPDF2.errors.PdfReadError as pe:
        print(f"读取PDF文件 {pdf_filepath} 时发生PdfReadError (文件可能已损坏或格式不受支持): {pe}")
        return f"读取PDF文件出错: {pe}"
    except Exception as e:
        print(f"读取PDF文件 {pdf_filepath} 时发生未知错误: {e}")
        return f"读取PDF文件出错: {e}"
    if not text_content.strip():
        print(f"提示: PDF文件 {pdf_filepath} 未能提取到文本，或者文件为空。")
        return "未能提取到文本或文件为空"
    return text_content

def read_all_policies_data(policies_base_path):
    combined_text = ""
    print(f"开始从 {policies_base_path} 读取政策文件...")
    if not os.path.isdir(policies_base_path):
        print(f"错误: 政策文件目录 {policies_base_path} 不存在或不是一个目录。")
        return ""

    for item_name in os.listdir(policies_base_path):
        item_path = os.path.join(policies_base_path, item_name)
        if os.path.isdir(item_path):
            meta_json_path = os.path.join(item_path, "meta.json")
            if os.path.exists(meta_json_path):
                print(f"  正在处理: {meta_json_path}")
                try:
                    with open(meta_json_path, 'r', encoding='utf-8') as f:
                        meta_data = json.load(f)
                        if isinstance(meta_data.get('content'), dict) and meta_data['content'].get('正文内容'):
                            combined_text += meta_data['content']['正文内容'] + "\n\n"
                        elif isinstance(meta_data.get('content'), str):
                            combined_text += meta_data['content'] + "\n\n"
                        else:
                            print(f"    提示: {meta_json_path} 中未找到 'content.正文内容' 或 'content' 字符串。")
                except json.JSONDecodeError:
                    print(f"    错误: 解析 {meta_json_path} 失败。跳过此文件。")
                except Exception as e:
                    print(f"    读取或处理 {meta_json_path} 时发生错误: {e}")

                attachments_path = os.path.join(item_path, "attachments")
                if os.path.isdir(attachments_path):
                    for attachment_filename in os.listdir(attachments_path):
                        attachment_filepath = os.path.join(attachments_path, attachment_filename)
                        file_text = ""
                        if attachment_filename.lower().endswith(".docx"):
                            print(f"    正在读取附件 (DOCX): {attachment_filepath}")
                            file_text = read_docx_file(attachment_filepath)
                        elif attachment_filename.lower().endswith(".pdf"):
                            print(f"    正在读取附件 (PDF): {attachment_filepath}")
                            file_text = read_pdf_file(attachment_filepath)
                        elif attachment_filename.lower().endswith(".doc"):
                            print(f"    提示: 检测到 .doc 文件 ({attachment_filename})，根据用户要求跳过处理。")
                            continue # 跳过 .doc 文件
                        
                        error_states = [
                            "文件未找到", "python-docx 库未安装", "读取文件出错", 
                            "未能提取到文本或文件为空", "无效的DOCX文件",
                            "PyPDF2库不可用", "读取PDF文件出错", "加密PDF无法解密"
                        ]
                        is_error_or_empty = False
                        if not file_text or not file_text.strip(): # 检查是否为空或只有空白
                            is_error_or_empty = True
                        else:
                            for state in error_states:
                                if state in file_text:
                                    is_error_or_empty = True
                                    break
                        
                        if not is_error_or_empty:
                            combined_text += file_text + "\n\n"
            else:
                print(f"  跳过目录 {item_path} (未找到 meta.json)")
    
    print(f"政策文件读取完毕。总字符数 (粗略): {len(combined_text)}")
    return combined_text

def get_answer_from_llm(question_text, document_text, model_name="qwen-plus"):
    if not client:
        print("错误: OpenAI 客户端未初始化。无法调用大模型 API。")
        return "LLM客户端未初始化"
    if not document_text or not document_text.strip():
        print("错误: 提供的文档内容为空。无法向LLM提问。")
        return "文档内容为空"

    max_doc_length = 15000 
    truncated_document_text = document_text
    if len(document_text) > max_doc_length:
        print(f"  提示: 文档内容过长 ({len(document_text)} chars)，将截断为 {max_doc_length} 字符输入给LLM。")
        truncated_document_text = document_text[:max_doc_length]

    prompt = f"请在以下提供的文本中找到问题 '{question_text}' 的答案。请只回答数字。如果找不到确切的数字答案，请回答 '未找到数字答案'。\n\n提供的文本：\n{truncated_document_text}"

    print(f"  发送给LLM的问题: {question_text}")

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {'role': 'system', 'content': '你是一个 внимательный (attentive) 的AI助手，专门负责从提供的文本中提取信息并严格按照指示回答问题。'},
                {'role': 'user', 'content': prompt}
            ],
            stream=True, 
            stream_options={"include_usage": True} 
        )
        
        ai_full_response_content = ""
        for chunk in completion:
            if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta and chunk.choices[0].delta.content:
                ai_full_response_content += chunk.choices[0].delta.content
        
        ai_response_content = ai_full_response_content.strip()
        print(f"  LLM原始回答 (流式接收完毕): {ai_response_content}")

        numbers_in_response = re.findall(r'\d+', ai_response_content)
        if numbers_in_response:
            return numbers_in_response[0]
        elif "未找到数字答案" in ai_response_content or "无法找到" in ai_response_content or "未能找到" in ai_response_content:
             return "未找到数字答案"
        else:
            print(f"  LLM的回答 '{ai_response_content}' 中未直接找到数字，且未明确说明未找到。将其视为 '未找到数字答案'。")
            return "未找到数字答案"

    except Exception as e:
        print(f"调用大模型API时发生错误: {e}")
        return f"LLM API调用失败: {e}"

if __name__ == '__main__':
    if not client:
        print("程序因 OpenAI 客户端初始化失败而退出。请检查 API Key 配置。")
        exit(1)

    policies_dir_path = "/Users/a1/study/爬虫/demo/AI-hallucination/src/data/policies"
    questions_csv_path = "/Users/a1/study/爬虫/demo/AI-hallucination/ai_evaluation_dataset_long.csv"
    output_csv_dir = os.path.dirname(questions_csv_path)
    output_csv_filename = os.path.splitext(os.path.basename(questions_csv_path))[0] + "_policies_llm_answers_v3.csv" # 更新输出文件名
    output_csv_path = os.path.join(output_csv_dir, output_csv_filename)

    print(f"问题CSV路径: {questions_csv_path}")
    print(f"政策文件目录: {policies_dir_path}")
    print(f"输出CSV路径: {output_csv_path}")

    combined_policies_text = read_all_policies_data(policies_dir_path)

    if not combined_policies_text.strip():
        print("错误: 未能从政策文件中读取到任何有效内容。程序退出。")
        exit(1)

    questions_data = read_questions_from_csv(questions_csv_path)
    if not questions_data:
        print("未能加载问题，程序退出。")
        exit(1)

    all_results = []

    for row_index, question_row in enumerate(questions_data):
        school_name = question_row.get('学校名称')
        metric_name = question_row.get('指标名称')
        
        if not school_name or not metric_name:
            print(f"警告: CSV文件第 {row_index + 2} 行缺少 '学校名称' 或 '指标名称'。跳过此行。")
            updated_row = question_row.copy()
            updated_row['AI答案'] = '输入数据不完整'
            all_results.append(updated_row)
            continue
            
        current_question_text = f"{school_name}的{metric_name}是多少？"
        print(f"\n正在处理问题 ({row_index + 1}/{len(questions_data)}): {current_question_text}")

        answer = get_answer_from_llm(current_question_text, combined_policies_text)
        print(f"  LLM找到的答案 (处理后): {answer}")
        
        updated_row = question_row.copy()
        if '待填充' not in updated_row:
            updated_row['待填充'] = '' 
        updated_row['AI答案'] = answer
        all_results.append(updated_row)

    if all_results:
        if questions_data:
            original_fieldnames = list(questions_data[0].keys())
            if 'AI答案' not in original_fieldnames:
                 fieldnames = original_fieldnames + ['AI答案']
            else: 
                 fieldnames = original_fieldnames
        else: 
            fieldnames = list(all_results[0].keys())

        try:
            with open(output_csv_path, mode='w', encoding='utf-8-sig', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_results)
            print(f"\n处理完成，结果已保存到: {output_csv_path}")
        except Exception as e:
            print(f"写入输出CSV文件 {output_csv_path} 时发生错误: {e}")
    else:
        print("没有结果可以写入CSV文件。")
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

# --- 新增的保存函数 ---
def save_combined_data(data, output_path):
    """保存数据到JSON文件，包含验证和原子写入"""
    def validate_json_data(data_to_validate):
        try:
            # 尝试序列化来检查是否有不可序列化的类型
            json.dumps(data_to_validate, ensure_ascii=False)
            return True
        except TypeError as e:
            print(f"错误: 数据中包含无法JSON序列化的类型 - {e}")
            # 尝试找出问题数据项 (如果数据是列表)
            if isinstance(data_to_validate, dict) and 'results' in data_to_validate and isinstance(data_to_validate['results'], list):
                for i, item in enumerate(data_to_validate['results']):
                    try:
                        json.dumps(item, ensure_ascii=False)
                    except TypeError:
                        print(f"  问题数据项索引 {i}: {str(item)[:100]}...") # 打印部分问题数据
            return False
        except Exception as e:
            print(f"JSON验证时发生未知错误: {e}")
            return False

    if not validate_json_data(data):
        print(f"错误: 提供给 save_combined_data 的数据未能通过JSON验证。文件 {output_path} 未保存。")
        return False

    temp_output_path = output_path + '.tmp'
    try:
        with open(temp_output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        # 验证写入的临时文件是否是有效的JSON
        with open(temp_output_path, 'r', encoding='utf-8') as f_check:
            json.load(f_check) # 如果这里抛出异常，说明写入的文件有问题
        
        os.replace(temp_output_path, output_path)
        print(f"成功: 数据已保存到 {output_path}")
        return True
    except json.JSONDecodeError as e:
        print(f"错误: 写入到临时文件 {temp_output_path} 的内容不是有效的JSON: {e}")
        if os.path.exists(temp_output_path):
            os.remove(temp_output_path)
        return False
    except Exception as e:
        print(f"保存JSON文件 {output_path} 时发生错误: {e}")
        if os.path.exists(temp_output_path):
            try:
                os.remove(temp_output_path)
            except OSError as oe:
                print(f"删除临时文件 {temp_output_path} 失败: {oe}")
        return False

# --- 新增的字数统计函数 ---
def count_characters_in_json_value(value):
    """递归统计JSON值中的字符数（仅计算字符串类型的值）。"""
    count = 0
    if isinstance(value, str):
        count += len(value)
    elif isinstance(value, list):
        for item in value:
            count += count_characters_in_json_value(item)
    elif isinstance(value, dict):
        for k, v in value.items():
            # 如果需要，也可以统计键的字符数
            # count += len(k)
            count += count_characters_in_json_value(v)
    return count

def count_total_characters_in_file(json_file_path):
    """读取JSON文件并统计其中所有文本内容的字符总数。"""
    if not os.path.exists(json_file_path):
        print(f"错误：用于计数的JSON文件未找到 {json_file_path}")
        return 0

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"错误：无法解析用于计数的JSON文件 {json_file_path}: {e}")
        return 0
    except Exception as e:
        print(f"读取用于计数的JSON文件时发生错误 {json_file_path}: {e}")
        return 0

    total_chars = count_characters_in_json_value(data)
    return total_chars
# --- 字数统计函数结束 ---

def read_all_policies_data(policies_base_path):
    combined_data_list = [] # 修改变量名以更清晰地表示它是一个列表
    print(f"正在递归读取 {policies_base_path} 所有 JSON 文件...")

    # 标准化处理函数
    def normalize_json(data, file_path): # file_path 参数现在未使用，但保留以备将来扩展
        """
        将不同结构 JSON 转换为统一格式:
        - 单个对象 → 放入列表
        - 数组 → 直接合并
        """
        if isinstance(data, list):
            # 确保列表中的每个项目都是字典，如果不是，则包装它
            return [{**item} if isinstance(item, dict) else {"__file_source": file_path, "value": item} 
                    for item in data]
        elif isinstance(data, dict):
            return [{**data, "__file_source": file_path}]
        else:
            # 对于非字典、非列表的顶层JSON结构 (例如，一个裸字符串或数字)
            return [{"__file_source": file_path, "value": data}]

    for root, _, files in os.walk(policies_base_path):
        for file_name in files:
            if file_name.endswith('.json') and file_name != "combined_data.json": # 避免读取自己生成的文件
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                        normalized = normalize_json(json_data, file_path)
                        combined_data_list.extend(normalized)
                except json.JSONDecodeError:
                    print(f"{file_path} 不是有效JSON文件或为空，已跳过。")
                except Exception as e:
                    print(f"处理 {file_path} 失败: {str(e)[:100]}... 已跳过。")

    # 构建最终的数据结构
    final_data_structure = {
        "total_items": len(combined_data_list),
        "data_types": list(set([type(d).__name__ for d in combined_data_list])), # 获取实际数据类型
        "results": combined_data_list
    }

    # 保存整合后的标准化数据
    output_path = os.path.join(policies_base_path, "combined_data.json")
    
    # 使用新的保存函数
    if save_combined_data(final_data_structure, output_path):
        return output_path # 返回的是文件路径
    else:
        print(f"未能成功保存 {output_path}")
        return None # 或其他表示失败的值

# 修改 get_answer_from_llm 函数，支持会话上下文
def get_answers_from_llm_with_context(questions_list, document_text, model_name="qwen-turbo-1101"):
    """使用单一上下文处理多个问题，避免重复发送文档内容"""
    if not client:
        print("错误: OpenAI 客户端未初始化。无法调用大模型 API。")
        return ["LLM客户端未初始化"] * len(questions_list)
    
    if not document_text or not document_text.strip():
        print("错误: 提供的文档内容为空。无法向LLM提问。")
        return ["文档内容为空"] * len(questions_list)
    
    # 检查文档长度
    max_doc_length = 900000  # 接近1M但留出一些空间给问题和回答
    truncated_document_text = document_text
    if len(document_text) > max_doc_length:
        print(f"  提示: 文档内容过长 ({len(document_text)} chars)，将截断为 {max_doc_length} 字符输入给LLM。")
        truncated_document_text = document_text[:max_doc_length]
    
    # 初始化消息列表，包含系统提示和文档内容
    messages = [
        {'role': 'system', 'content': '你是一个分析中国大学数据的AI助手，专门负责从提供的文本中提取信息并严格按照指示回答问题。'},
        {'role': 'user', 'content': f"以下是你需要参考的文档内容，请记住这些信息以回答后续问题：\n\n{truncated_document_text}"},
        {'role': 'assistant', 'content': "我是一个专门解答关于中国教育政策的AI助手。我已分析了提供的文档内容，准备回答您的问题。"}
    ]
    
    # 创建一个会话，发送文档内容
    try:
        print("  正在将文档内容发送给LLM作为上下文...")
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=False
        )
        
        # 确认文档已被接收
        if not completion.choices or not completion.choices[0].message:
            print("  警告: LLM未能正确接收文档内容")
            return ["LLM未能接收文档内容"] * len(questions_list)
            
        # 存储所有答案
        all_answers = []
        
        # 逐个发送问题并获取答案
        for question_text in questions_list:
            print(f"  发送问题给LLM: {question_text}")
            
            # 添加当前问题到消息列表
            current_messages = messages.copy()
            current_messages.append({'role': 'user', 'content': f"我将为你提供一个问题，问题如下'{question_text}'，问题包含了某个大学和某个指标，请你在先前提供的文本中统计对应的大学相关指标的信息，并进行计算得出统计后的答案。请只回答数字。如果找不到确切的数字答案，请回答 '未找到数字答案'"})
            
            # 发送问题
            question_completion = client.chat.completions.create(
                model=model_name,
                messages=current_messages,
                stream=True,
                stream_options={"include_usage": True}
            )
            
            # 收集回答
            ai_full_response_content = ""
            for chunk in question_completion:
                if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    ai_full_response_content += chunk.choices[0].delta.content
            
            ai_response_content = ai_full_response_content.strip()
            print(f"  LLM原始回答 (流式接收完毕): {ai_response_content}")
            
            # 处理回答
            numbers_in_response = re.findall(r'\d+', ai_response_content)
            if numbers_in_response:
                answer = numbers_in_response[0]
            elif "未找到数字答案" in ai_response_content or "无法找到" in ai_response_content or "未能找到" in ai_response_content:
                answer = "未找到数字答案"
            else:
                print(f"  LLM的回答 '{ai_response_content}' 中未直接找到数字，且未明确说明未找到。将其视为 '未找到数字答案'。")
                answer = "未找到数字答案"
                
            all_answers.append(answer)
            
            # 将回答添加到消息历史中，以便下一个问题可以参考
            messages.append({'role': 'user', 'content': f"请在之前提供的文本中找到问题 '{question_text}' 的答案。请只回答数字。如果找不到确切的数字答案，请回答 '未找到数字答案'。"})
            messages.append({'role': 'assistant', 'content': ai_response_content})
        
        return all_answers
            
    except Exception as e:
        print(f"调用大模型API时发生错误: {e}")
        return [f"LLM API调用失败: {e}"] * len(questions_list)

if __name__ == '__main__':
    if not client:
        print("程序因 OpenAI 客户端初始化失败而退出。请检查 API Key 配置。")
        exit(1)
    # 获取当前脚本所在目录作为基准
    current_script_dir = os.path.dirname(os.path.abspath(__file__))

    # 计算项目根目录（假设AIquest是在项目根目录的子目录）
    project_root = os.path.dirname(current_script_dir)

    # 基于项目根目录构建相对路径
    policies_dir_path = os.path.join(project_root, "src", "data", "policies")
    questions_csv_path = os.path.join(project_root, "ai_evaluation_dataset_long.csv")
    # policies_dir_path = "/Users/a1/study/爬虫/demo/AI-hallucination/src/data/policies"
    # questions_csv_path = "/Users/a1/study/爬虫/demo/AI-hallucination/ai_evaluation_dataset_long.csv"
    output_csv_dir = os.path.dirname(questions_csv_path)
    output_csv_filename = os.path.splitext(os.path.basename(questions_csv_path))[0] + "_llm_answers.csv" # 更新输出文件名
    output_csv_path = os.path.join(output_csv_dir, output_csv_filename)

    print(f"问题CSV路径: {questions_csv_path}")
    print(f"政策文件目录: {policies_dir_path}")
    print(f"输出CSV路径: {output_csv_path}")

    # read_all_policies_data 现在返回的是 combined_data.json 的路径或 None
    combined_json_file_path = read_all_policies_data(policies_dir_path)

    if not combined_json_file_path:
        print("错误: 未能生成或找到 combined_data.json 文件。程序退出。")
        exit(1)
    
    # 统计生成后的 combined_data.json 文件中的字符数
    print(f"\n正在统计 {combined_json_file_path} 中的字符数...")
    total_chars_in_combined_file = count_total_characters_in_file(combined_json_file_path)
    if total_chars_in_combined_file > 0:
        print(f"文件 '{os.path.basename(combined_json_file_path)}' 中的总字符数（仅计算文本内容）为: {total_chars_in_combined_file}")
    else:
        print(f"未能统计文件 '{os.path.basename(combined_json_file_path)}' 中的字符数，或文件为空/读取失败。")

    # 读取 combined_data.json 的内容以供 LLM 使用
    combined_policies_text_content = ""
    try:
        with open(combined_json_file_path, 'r', encoding='utf-8') as f_combined:
            # 如果LLM需要整个JSON的字符串表示
            # combined_policies_text_content = f_combined.read()
            
            # 或者，如果LLM只需要 'results' 部分的文本内容，可以这样处理：
            data_for_llm = json.load(f_combined)
            temp_text_list = []
            def extract_strings_for_llm(value):
                if isinstance(value, str):
                    temp_text_list.append(value)
                elif isinstance(value, list):
                    for item_in_list in value:
                        extract_strings_for_llm(item_in_list)
                elif isinstance(value, dict):
                    for v_in_dict in value.values():
                        extract_strings_for_llm(v_in_dict)
            
            if 'results' in data_for_llm:
                extract_strings_for_llm(data_for_llm['results'])
            combined_policies_text_content = "\n".join(temp_text_list)

    except Exception as e:
        print(f"读取 {combined_json_file_path} 以供LLM使用时发生错误: {e}")
        exit(1)

    if not combined_policies_text_content.strip():
        print(f"错误: 从 {combined_json_file_path} 中未能读取到任何有效内容供LLM使用。程序退出。")
        exit(1)

    questions_data = read_questions_from_csv(questions_csv_path)
    if not questions_data:
        print("未能加载问题，程序退出。")
        exit(1)

    # 准备所有问题
    all_questions = []
    for row_index, question_row in enumerate(questions_data):
        school_name = question_row.get('学校名称')
        metric_name = question_row.get('指标名称')
        
        if not school_name or not metric_name:
            print(f"警告: CSV文件第 {row_index + 2} 行缺少 '学校名称' 或 '指标名称'。跳过此行。")
            all_questions.append(None)  # 占位，保持索引一致
        else:
            current_question_text = f"{school_name}的{metric_name}是多少？"
            all_questions.append(current_question_text)
    
    # 过滤掉None值，只保留有效问题
    valid_questions = [q for q in all_questions if q is not None]
    valid_indices = [i for i, q in enumerate(all_questions) if q is not None]
    
    print(f"\n共有 {len(valid_questions)} 个有效问题需要处理")
    print("正在使用单一上下文批量处理所有问题...")
    
    # 使用新函数批量获取答案
    answers = get_answers_from_llm_with_context(valid_questions, combined_policies_text_content)
    
    # 将答案填回结果列表
    all_results = []
    answer_index = 0
    
    for row_index, question_row in enumerate(questions_data):
        updated_row = question_row.copy()
        if row_index in valid_indices:
            # 这是一个有效问题，使用获取的答案
            updated_row['AI答案'] = answers[answer_index]
            answer_index += 1
        else:
            # 这是一个无效问题，标记为数据不完整
            updated_row['AI答案'] = '输入数据不完整'
        
        if '待填充' not in updated_row:
            updated_row['待填充'] = ''
            
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
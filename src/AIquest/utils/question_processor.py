"""问题处理和答案生成"""
import csv
import os
from src.AIquest.config import OUTPUT_CONFIG, QUESTION_TEMPLATES


class QuestionProcessor:
    """问题处理和答案生成"""
    
    def __init__(self, llm_client, data_reader):
        self.llm_client = llm_client
        self.data_reader = data_reader
    
    def filter_questions_by_metric(self, questions_csv_path, metric_name):
        """筛选出特定指标的问题"""
        questions_data = []
        try:
            with open(questions_csv_path, mode='r', encoding=OUTPUT_CONFIG['file_encoding']) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get('指标名称') == metric_name:
                        questions_data.append(row)
        except Exception as e:
            print(f"  读取问题CSV文件失败: {e}")
            return []
        
        print(f"  找到 {len(questions_data)} 个关于 '{metric_name}' 的问题")
        return questions_data
    
    def process_metric_questions(self, metric_questions, consolidated_data_path, output_csv_path, metric_name):
        """处理特定指标的问题"""
        if not metric_questions:
            print(f"  没有关于 '{metric_name}' 的问题需要处理")
            return False
        
        # 提取文本内容供LLM使用
        document_text = self.data_reader.extract_text_content(consolidated_data_path)
        if not document_text.strip():
            print(f"  错误: 无法从 {consolidated_data_path} 提取有效文本内容")
            return False
        
        # 准备问题列表
        questions_list = []
        for question_row in metric_questions:
            school_name = question_row.get('学校名称')
            metric_name_in_question = question_row.get('指标名称')
            if school_name and metric_name_in_question:
                question_text = self._format_question(school_name, metric_name_in_question)
                questions_list.append(question_text)
        
        if not questions_list:
            print(f"  没有有效的问题需要处理")
            return False
        
        print(f"  正在处理 {len(questions_list)} 个关于 '{metric_name}' 的问题")
        
        # 获取LLM答案
        answers = self.llm_client.get_answers_for_metric(
            questions_list, document_text, metric_name
        )
        
        if len(answers) != len(questions_list):
            print(f"  警告: 答案数量({len(answers)})与问题数量({len(questions_list)})不匹配")
            return False
        
        # 填充结果
        results = []
        for i, question_row in enumerate(metric_questions):
            updated_row = question_row.copy()
            if i < len(answers):
                updated_row['AI答案'] = answers[i]
            else:
                updated_row['AI答案'] = '处理失败'
            results.append(updated_row)
        
        # 保存结果
        return self._save_results(results, output_csv_path)
    
    def _format_question(self, school_name, metric_name, template_type='default'):
        """格式化问题文本"""
        template = QUESTION_TEMPLATES.get(template_type, QUESTION_TEMPLATES['default'])
        return template.format(school_name=school_name, metric_name=metric_name)
    
    def _save_results(self, results, output_csv_path):
        """保存结果到CSV文件"""
        if not results:
            print("  没有结果可以保存")
            return False
        
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
            
            # 获取字段名
            fieldnames = list(results[0].keys())
            if 'AI答案' not in fieldnames:
                fieldnames.append('AI答案')
            
            with open(output_csv_path, mode='w', encoding=OUTPUT_CONFIG['file_encoding'], newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            
            print(f"  成功保存 {len(results)} 条结果到: {output_csv_path}")
            return True
            
        except Exception as e:
            print(f"  保存结果失败: {e}")
            return False
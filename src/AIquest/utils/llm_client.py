"""LLM客户端管理"""
import configparser
import os
import re
from openai import OpenAI
from src.AIquest.config import LLM_CONFIG, METRIC_CATEGORIES, METRIC_KEYWORDS


class LLMClient:
    """LLM客户端管理类"""
    
    def __init__(self, config_path=None):
        self.client = self._init_client(config_path)
        self.model_name = LLM_CONFIG['model_name']
        self.max_doc_length = LLM_CONFIG['max_doc_length']
    
    def _init_client(self, config_path):
        """初始化OpenAI客户端"""
        if config_path is None:
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(current_dir, 'config.ini')
        
        config = configparser.ConfigParser()
        api_key = None
        
        if os.path.exists(config_path):
            config.read(config_path)
            api_key = config.get('DEFAULT', 'DASHSCOPE_API_KEY', fallback=None)
        
        if not api_key:
            print("警告: 未在配置文件中找到 DASHSCOPE_API_KEY")
            return None
        
        return OpenAI(
            api_key=api_key,
            base_url=LLM_CONFIG['base_url']
        )
    
    def get_answers_for_metric(self, questions_list, document_text, metric_name):
        """为特定指标获取答案"""
        if not self.client:
            print("错误: OpenAI 客户端未初始化")
            return ["LLM客户端未初始化"] * len(questions_list)
        
        if not document_text or not document_text.strip():
            print("错误: 提供的文档内容为空")
            return ["文档内容为空"] * len(questions_list)
        
        # 截断文档内容
        truncated_document_text = self._truncate_document(document_text)
        
        # 根据指标类型定制系统提示
        system_prompt = self._get_system_prompt_for_metric(metric_name)
        
        # 初始化消息列表
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f"以下是关于 '{metric_name}' 的数据，请记住这些信息：\n\n{truncated_document_text}"},
            {'role': 'assistant', 'content': f"我已经分析了关于 '{metric_name}' 的数据，准备回答相关问题。"}
        ]
        
        try:
            # 确认文档已被接收
            print(f"  正在将 '{metric_name}' 相关数据发送给LLM...")
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=False
            )
            
            if not completion.choices or not completion.choices[0].message:
                print("  警告: LLM未能正确接收文档内容")
                return ["LLM未能接收文档内容"] * len(questions_list)
            
            # 处理每个问题
            all_answers = []
            for question_text in questions_list:
                answer = self._process_single_question(messages.copy(), question_text, metric_name)
                all_answers.append(answer)
                
                # 更新消息历史
                messages.append({'role': 'user', 'content': self._get_question_prompt(question_text, metric_name)})
                messages.append({'role': 'assistant', 'content': answer})
            
            return all_answers
            
        except Exception as e:
            print(f"调用LLM API时发生错误: {e}")
            return [f"LLM API调用失败: {e}"] * len(questions_list)
    
    def _truncate_document(self, document_text):
        """截断文档内容"""
        if len(document_text) > self.max_doc_length:
            print(f"  文档内容过长 ({len(document_text)} chars)，将截断为 {self.max_doc_length} 字符")
            return document_text[:self.max_doc_length]
        return document_text
    
    def _get_system_prompt_for_metric(self, metric_name):
        """根据指标类型获取系统提示"""
        if metric_name in METRIC_CATEGORIES['subject_metrics']:
            if 'ESI' in metric_name:
                return """你是一个专门分析ESI学科排名数据的AI助手。
ESI（Essential Science Indicators）是基于Web of Science数据库的学科排名系统。
请在数据中准确查找和统计ESI相关学科信息。
重点关注：进入ESI前1%或前1‰的学科名称和数量。
只返回准确的数字答案。"""
            elif '双一流' in metric_name:
                return """你是一个专门分析国家双一流学科建设数据的AI助手。
双一流指"世界一流大学和一流学科建设"，是国家重大教育政策。
请在教育部政策数据中准确查找和统计双一流学科信息。
重点关注：入选国家双一流建设的学科名称和数量。
只返回准确的数字答案。"""
            elif '教育部评估A类' in metric_name:
                return """你是一个专门分析教育部学科评估数据的AI助手。
教育部学科评估是对全国具有博士或硕士学位授予权的一级学科的整体水平评估。
A类学科包括：A+、A、A-三个等级，代表该学科在全国排名前10%。
请在学科评估数据中准确查找和统计A类学科信息。
重点关注：获得A+、A、A-评级的学科名称和数量。
只返回准确的数字答案。"""
            elif '软科' in metric_name:
                return """你是一个专门分析软科中国最好学科排名数据的AI助手。
软科排名是重要的学科评价体系，前10%表示学科实力较强。
请在数据中准确查找和统计软科排名相关信息。
重点关注：进入软科排名前10%的学科名称和数量。
只返回准确的数字答案。"""
            else:
                return """你是一个专门分析中国大学学科数据的AI助手。
请准确统计和计算学科相关指标，重点关注学科数量。
只返回准确的数字答案。"""
        
        elif metric_name in METRIC_CATEGORIES['major_metrics']:
            if '专业认证' in metric_name:
                return """你是一个专门分析高等教育专业认证数据的AI助手。
专业认证包括工程教育认证、师范类专业认证、医学教育认证等。
请在教育部政策数据和专业数据中准确查找和统计通过专业认证的本科专业信息。
重点关注：通过各类专业认证的本科专业名称和数量。
只返回准确的数字答案。"""
            elif '一流本科专业' in metric_name:
                return """你是一个专门分析一流本科专业建设点数据的AI助手。
一流本科专业建设点分为国家级和省级两个层次。
请在教育部政策数据中准确查找和统计一流本科专业建设点信息。
重点关注：获批的国家级或省级一流本科专业建设点名称和数量。
只返回准确的数字答案。"""
            else:
                return """你是一个专门分析中国大学本科专业数据的AI助手。
请在教育部政策数据和专业数据中准确统计和计算本科专业相关指标。
重点关注：专业数量统计。
只返回准确的数字答案。"""
        
        else:
            return "你是一个专门分析中国大学数据的AI助手。请准确统计和计算相关指标。只返回准确的数字答案。"
    
    def _get_question_prompt(self, question_text, metric_name):
        """根据指标类型获取优化的问题提示"""
        base_prompt = f"问题：{question_text}\n\n"
        
        # 获取指标关键词
        keywords = METRIC_KEYWORDS.get(metric_name, [])
        keywords_str = "、".join(keywords) if keywords else metric_name
        
        if metric_name == 'ESI前1%学科数量':
            return base_prompt + f"""请在数据中查找ESI相关信息，重点关注以下关键词：{keywords_str}。
查找进入ESI前1%的学科，并统计数量。
如果数据中明确提到ESI前1%学科，请统计具体数量。
只返回数字答案，如果找不到相关信息，请回答"0"。"""
        
        elif metric_name == 'ESI前1‰学科数量':
            return base_prompt + f"""请在数据中查找ESI相关信息，重点关注以下关键词：{keywords_str}。
查找进入ESI前1‰（千分之一）的学科，并统计数量。
如果数据中明确提到ESI前1‰学科，请统计具体数量。
只返回数字答案，如果找不到相关信息，请回答"0"。"""
        
        elif metric_name == '国家"双一流"学科数量':
            return base_prompt + f"""请在教育部政策数据中查找双一流相关信息，重点关注以下关键词：{keywords_str}。
查找入选国家"双一流"学科建设的学科，并统计数量。
注意区分"双一流大学"和"双一流学科"，这里只统计学科数量。
只返回数字答案，如果找不到相关信息，请回答"0"。"""
        
        elif metric_name == '教育部评估A类学科数量':
            return base_prompt + f"""请在学科评估数据中查找教育部评估相关信息，重点关注以下关键词：{keywords_str}。
查找在教育部学科评估中获得A类评级（A+、A、A-）的学科，并统计数量。
注意：
- A+表示前2%或前2名（该学科全国排名最高）
- A表示前2%-5%
- A-表示前5%-10%
- 这三个等级统称为A类学科
如果数据中明确提到学科评估A+、A、A-等级，请统计具体数量。
只返回数字答案，如果找不到相关信息，请回答"0"。"""
        
        elif metric_name == '软科"中国最好学科"排名前10%学科数量':
            return base_prompt + f"""请在数据中查找软科排名相关信息，重点关注以下关键词：{keywords_str}。
查找在软科"中国最好学科"排名中进入前10%的学科，并统计数量。
只返回数字答案，如果找不到相关信息，请回答"0"。"""
        
        elif metric_name == '本科专业总数':
            return base_prompt + f"""请在教育部政策数据和专业数据中查找本科专业相关信息，重点关注以下关键词：{keywords_str}。
统计该学校的本科专业总数，包括所有本科专业。
只返回数字答案，如果找不到相关信息，请回答"0"。"""
        
        elif metric_name == '本科专业认证通过数':
            return base_prompt + f"""请在教育部政策数据中查找专业认证相关信息，重点关注以下关键词：{keywords_str}。
查找通过各类专业认证（如工程教育认证、师范类专业认证等）的本科专业，并统计数量。
只返回数字答案，如果找不到相关信息，请回答"0"。"""
        
        elif metric_name == '国家级一流本科专业建设点':
            return base_prompt + f"""请在教育部政策数据中查找一流本科专业相关信息，重点关注以下关键词：{keywords_str}。
查找获批国家级一流本科专业建设点的专业，并统计数量。
注意区分国家级和省级，这里只统计国家级。
只返回数字答案，如果找不到相关信息，请回答"0"。"""
        
        elif metric_name == '省级一流本科专业建设点':
            return base_prompt + f"""请在教育部政策数据中查找一流本科专业相关信息，重点关注以下关键词：{keywords_str}。
查找获批省级一流本科专业建设点的专业，并统计数量。
注意区分国家级和省级，这里只统计省级（或省一流）。
只返回数字答案，如果找不到相关信息，请回答"0"。"""
        
        else:
            return base_prompt + f"请在数据中查找 {metric_name} 相关信息并统计数量。只返回数字答案。如果找不到，请回答'0'。"
    
    def _process_single_question(self, messages, question_text, metric_name):
        """处理单个问题"""
        print(f"  处理问题: {question_text}")
        
        current_messages = messages.copy()
        question_prompt = self._get_question_prompt(question_text, metric_name)
        current_messages.append({'role': 'user', 'content': question_prompt})
        
        # 获取答案
        question_completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=current_messages,
            stream=True,
            stream_options={"include_usage": True}
        )
        
        # 收集回答
        ai_response = ""
        for chunk in question_completion:
            if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta and chunk.choices[0].delta.content:
                ai_response += chunk.choices[0].delta.content
        
        ai_response = ai_response.strip()
        print(f"    LLM回答: {ai_response}")
        
        # 解析答案
        return self._parse_answer(ai_response, metric_name)
    
    def _parse_answer(self, ai_response, metric_name):
        """解析AI回答，针对指标优化"""
        # 查找数字
        numbers = re.findall(r'\d+', ai_response)
        if numbers:
            # 对于某些指标，可能需要特殊处理
            if metric_name in ['ESI前1%学科数量', 'ESI前1‰学科数量']:
                # ESI指标通常数量不会太大，选择最小的合理数字
                valid_numbers = [int(n) for n in numbers if int(n) <= 50]  # ESI学科数一般不超过50
                if valid_numbers:
                    return str(min(valid_numbers))
            elif metric_name == '教育部评估A类学科数量':
                # 教育部评估A类学科数量通常不会太大，一般不超过30个
                valid_numbers = [int(n) for n in numbers if int(n) <= 30]
                if valid_numbers:
                    return str(min(valid_numbers))
            
            return numbers[0]
        
        # 检查是否明确说明未找到或为0
        if any(keyword in ai_response for keyword in ["未找到", "无法找到", "没有找到", "不存在", "为0", "是0", "等于0"]):
            return "0"
        
        # 默认情况
        print(f"    警告: 无法从回答 '{ai_response}' 中提取数字，标记为0")
        return "0"
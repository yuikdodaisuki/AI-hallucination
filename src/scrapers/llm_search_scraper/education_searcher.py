"""
教育数据搜索器 - 腾讯云DeepSeek联网搜索版本
"""
import json
import os
import time
import random
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI
from openai.types.chat.chat_completion import Choice
from education_search_configs import education_manager, EducationSearchConfig, get_university_official_website, get_university_aliases

class EducationDataSearcher:
    """教育数据搜索器 - 腾讯云DeepSeek联网搜索版本"""
    
    def __init__(self, client: OpenAI, target_year: int = None, base_output_dir: str = None):
        self.client = client
        self.education_manager = education_manager
        self.target_year = target_year or datetime.now().year
        
        # 输出目录
        if base_output_dir:
            self.base_output_dir = base_output_dir
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.base_output_dir = os.path.join(current_dir, "education_search_results")
        
        # 速率限制
        self.rpm_limit = 3
        self.request_interval = 60 / self.rpm_limit + 2
        self.last_request_time = 0
        
        print(f"📁 输出目录: {self.base_output_dir}")
        print(f"📅 目标年份: {self.target_year}")
        print(f"🔍 使用腾讯云DeepSeek联网搜索")

    # =============================================================================
    # 🔥 核心搜索方法 🔥
    # =============================================================================
    
    def search_single_university_metric(self, config_name: str, university: str) -> Dict[str, Any]:
        """🔥 修改：支持多源搜索的单个大学指标搜索 🔥"""
        print(f"\n🔍 多源搜索 {university} - {config_name} (截止{self.target_year}年)")
        
        try:
            # 获取配置和官网
            config = self.education_manager.get_config(config_name)
            official_website = get_university_official_website(university)
            
            # 🔥 使用多源搜索消息创建 🔥
            print(f"🌐 启用多源权威搜索模式")
            if official_website:
                print(f"🏛️ 官网: {official_website}")
            
            messages = education_manager.create_messages_with_multi_source_search(
                config_name, university, self.target_year
            )
            
            # 执行搜索
            result_content, sources, iterations = self._execute_search(messages, config)
            
            if not result_content:
                return self._create_error_result(university, config_name, "多源搜索未完成")
            
            print(f"🔍 搜索完成，发现 {len(sources)} 个数据源")
            
            # 验证和处理结果
            return self._process_search_result(
                result_content, university, config_name, official_website, sources, iterations
            )
            
        except Exception as e:
            print(f"  ❌ 多源搜索失败: {e}")
            return self._create_error_result(university, config_name, str(e))
    
    def _execute_search(self, messages: List[Dict], config: EducationSearchConfig) -> Tuple[Optional[str], List[str], int]:
        """🔥 修改：使用腾讯云DeepSeek联网搜索 🔥"""
        iteration = 0
        all_sources = []
        final_result_content = None
        
        try:
            iteration = 1
            print(f"  第 {iteration} 轮搜索...")
            print(f"  🔍 使用腾讯云DeepSeek联网搜索...")
            
            # 🔥 直接调用，使用联网搜索 🔥
            choice = self._chat_with_retry(messages, config)
            
            # 🔥 直接获取搜索结果 🔥
            final_result_content = choice.message.content
            print(f"    ✅ 获得搜索结果: {len(final_result_content)} 字符")
            
            # 简单的源提取
            all_sources = ["腾讯云DeepSeek联网搜索"]
            
            # 🔥 检查是否包含搜索标识 🔥
            if any(indicator in final_result_content for indicator in ["搜索", "查找", "根据", "显示", "数据显示"]):
                all_sources.append("自动联网搜索")
            
        except Exception as e:
            print(f"    ❌ 搜索失败: {e}")
        
        return final_result_content, all_sources, iteration
    
    def _process_search_result(self, result_content: str, university: str, config_name: str, 
                              official_website: str, sources: List[str], iterations: int) -> Dict[str, Any]:
        """处理搜索结果 - 简化版，移除LLM验证"""
        print(f"  ✅ 搜索完成，开始验证...")
        
        # 基础验证
        name_verified, name_msg = self._verify_university_name(result_content, university)
        source_verified = self._verify_official_source(result_content, official_website) if official_website else True
        data_value = self._extract_data_value(result_content, university, config_name)
        
        print(f"  📝 学校验证: {'✅' if name_verified else '❌'} - {name_msg}")
        print(f"  🏛️ 官网验证: {'✅' if source_verified else '❌'}")
        print(f"  🔢 数据值: {data_value}")
        print(f"  📄 原始回答: {len(result_content)} 字符")
        
        # 🔥 简化质量判断 🔥
        quality_score = 0
        if name_verified: quality_score += 35
        if source_verified: quality_score += 35
        if data_value and "需要人工核查" not in data_value: quality_score += 30
        
        # 需要人工核查的条件
        needs_review = (
            not name_verified or 
            (official_website and not source_verified) or 
            "需要人工核查" in data_value
        )
        
        return {
            # 🔥 基础信息 🔥
            "university": university,
            "metric": config_name,
            "target_year": self.target_year,
            "data_value": data_value,
            "official_website": official_website,
            
            # 🔥 验证信息 🔥
            "name_verification": name_verified,
            "name_verification_details": name_msg,
            "official_source_verified": source_verified,
            "data_sources": sources,
            
            # 🔥 核心：完整的原始LLM回答 🔥
            "llm_raw_response": result_content,  # 完整保存LLM原始回答
            "response_length": len(result_content),  # 回答长度
            "is_response_complete": not result_content.endswith("..."),  # 检查是否被截断
            
            # 🔥 原始数据 🔥
            "search_result": result_content,  # 保持向后兼容
            "search_iterations": iterations,
            "data_quality": f"质量得分:{quality_score}/100",
            "requires_manual_review": needs_review,
            "search_timestamp": datetime.now().isoformat()
        }

    # =============================================================================
    # 🔥 验证方法 - 基础验证 🔥
    # =============================================================================
    
    def _verify_university_name(self, result_content: str, target_university: str) -> Tuple[bool, str]:
        """简化的学校名称验证"""
        # 获取有效名称
        alias_info = get_university_aliases(target_university)
        valid_names = alias_info.get("search_names", [target_university])
        
        # 检查是否包含有效名称
        for valid_name in valid_names:
            if valid_name in result_content:
                if valid_name != target_university:
                    return True, f"验证通过（匹配历史名称: {valid_name}）"
                else:
                    return True, "验证通过"
        
        return False, f"未明确提到'{target_university}'"
    
    def _verify_official_source(self, result_content: str, official_website: str) -> bool:
        """🔥 修改：更加灵活的数据源验证 🔥"""
        if not result_content:
            return False
        
        # 🔥 第一层：检查官网域名 🔥
        if official_website and official_website in result_content:
            return True
        
        # 🔥 第二层：检查政府权威网站 🔥
        government_sources = [
            'moe.gov.cn',      # 教育部
            'gdedu.gov.cn',    # 广东省教育厅
            'gov.cn',          # 政府网站通用域名
        ]
        
        for source in government_sources:
            if source in result_content:
                print(f"    🏛️ 检测到政府权威源: {source}")
                return True
        
        # 🔥 第三层：检查权威教育机构 🔥
        authoritative_education = [
            'heec.edu.cn',     # 高等教育评估中心
            'ceeaa.org.cn',    # 工程教育认证
            'camea.org.cn',    # 医学教育认证
            'clarivate.com',   # 科睿唯安
            'webofscience.com' # Web of Science
        ]
        
        for source in authoritative_education:
            if source in result_content:
                print(f"    🎓 检测到权威教育机构: {source}")
                return True
        
        # 🔥 第四层：检查权威媒体（条件性认可）🔥
        authoritative_media = [
            'eol.cn',          # 中国教育在线
            'chinaedu.edu.cn', # 中国教育
            'people.com.cn',   # 人民网
            'xinhuanet.com',   # 新华网
            'china.com.cn'     # 中国网
        ]
        
        for source in authoritative_media:
            if source in result_content:
                # 媒体源需要额外检查是否包含具体数据
                if any(indicator in result_content for indicator in ['获奖', '奖项', '成果', '名单', '公布']):
                    print(f"    📰 检测到权威媒体报道: {source}")
                    return True
        
        # 🔥 第五层：检查学校域名特征 🔥
        edu_domains = re.findall(r'[a-zA-Z0-9.-]+\.edu\.cn', result_content)
        if edu_domains:
            print(f"    🏫 检测到教育机构网站: {edu_domains}")
            return True
        
        print(f"    ⚠️ 未找到明确的权威数据源")
        return False

    def _extract_data_value(self, result_content: str, university: str, config_name: str) -> str:
        """🔥 改进数据提取 - 支持多种表达方式 🔥"""
        
        # 获取历史名称用于匹配
        alias_info = get_university_aliases(university)
        all_names = [university] + alias_info.get("historical_names", [])
        
        # 🔥 更全面的数字提取模式 🔥
        patterns = []
        
        # 针对每个可能的学校名称构建模式
        for name in all_names:
            patterns.extend([
                rf'{re.escape(name)}.*?获得.*?(\d+).*?项',
                rf'{re.escape(name)}.*?共.*?(\d+).*?项',
                rf'{re.escape(name)}.*?(\d+).*?个.*?奖',
                rf'{re.escape(name)}.*?(\d+).*?项.*?奖',
                rf'{re.escape(name)}.*?荣获.*?(\d+)',
            ])
        
        # 通用模式
        patterns.extend([
            r'获得.*?(\d+).*?项',
            r'共.*?(\d+).*?项.*?(教学成果奖|奖项)',
            r'(\d+).*?项.*?(省级|教学成果奖)',
            r'(特等奖|一等奖|二等奖).*?(\d+).*?项',
            r'总计.*?(\d+).*?项',
            r'累计.*?(\d+).*?项',
            r'(\d+).*?个.*?奖项'
        ])
        
        # 检查明确的"无获奖"表述
        no_award_patterns = [
            r'没有.*?(获得|获奖)',
            r'未.*?(获得|获奖)',
            r'无.*?(获奖|奖项)',
            r'0.*?项',
            r'暂无.*?(获奖|奖项)'
        ]
        
        for pattern in no_award_patterns:
            if re.search(pattern, result_content, re.IGNORECASE):
                return "0"
        
        # 提取数字
        extracted_numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, result_content, re.IGNORECASE)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        # 处理多个捕获组的情况
                        for item in match:
                            if item.isdigit():
                                extracted_numbers.append(int(item))
                    else:
                        if match.isdigit():
                            extracted_numbers.append(int(match))
        
        # 合理性检查
        reasonable_range = {
            'national_teaching_awards': (0, 10),
            'provincial_teaching_awards': (0, 50),
            'youth_teacher_competition': (0, 20),
            'esi_1_percent': (0, 30),
            'national_first_class_majors': (0, 50),
            'provincial_first_class_majors': (0, 100)
        }
        
        min_val, max_val = reasonable_range.get(config_name, (0, 200))
        valid_numbers = [n for n in extracted_numbers if min_val <= n <= max_val]
        
        if valid_numbers:
            # 如果有多个合理数字，选择最大的（通常是累计总数）
            return str(max(valid_numbers))
        elif extracted_numbers:
            # 如果有数字但超出合理范围，选择最小的并标注需要核查
            min_number = min(extracted_numbers)
            return f"{min_number}（需要人工核查-数值可能偏大）"
        
        return "需要人工核查-未找到明确数值"
    
    def _extract_sources_from_query(self, query: str) -> List[str]:
        """提取数据源"""
        sources = []
        if "site:" in query:
            sources.append("官网搜索")
        if "ESI" in query:
            sources.append("ESI数据库")
        if "教育部" in query:
            sources.append("教育部")
        return sources

    # =============================================================================
    # 🔥 工具方法 🔥
    # =============================================================================
    
    def _create_error_result(self, university: str, config_name: str, error_msg: str) -> Dict[str, Any]:
        """创建错误结果"""
        return {
            "university": university,
            "metric": config_name,
            "target_year": self.target_year,
            "data_value": None,
            "error": error_msg,
            "requires_manual_review": True,
            "data_quality": "质量得分:0/100",
            "search_timestamp": datetime.now().isoformat()
        }
    
    def _chat_with_retry(self, messages: List[Dict], config: EducationSearchConfig, max_attempts: int = 3) -> Choice:
        """🔥 修改：使用腾讯云DeepSeek API的联网搜索 🔥"""
        for attempt in range(max_attempts):
            try:
                # 速率限制
                current_time = time.time()
                if current_time - self.last_request_time < self.request_interval:
                    time.sleep(self.request_interval)
                self.last_request_time = time.time()
                
                # 🔥 使用腾讯云DeepSeek的联网搜索参数 🔥
                completion = self.client.chat.completions.create(
                    model=config.model,
                    messages=messages,
                    temperature=config.temperature,
                    max_tokens=800,  # 适当限制token数量
                    extra_body={
                        "enable_search": True  # 🔥 启用腾讯云DeepSeek联网搜索 🔥
                    }
                )
                return completion.choices[0]
                
            except Exception as e:
                print(f"    ❌ API调用失败: {e}")
                if attempt < max_attempts - 1:
                    wait_time = 2 ** attempt + random.uniform(1, 3)
                    print(f"    ⏰ {wait_time:.1f}秒后重试")
                    time.sleep(wait_time)
                else:
                    raise e
        
        raise Exception(f"API请求失败，已尝试 {max_attempts} 次")

    def test_online_search_capability(self, university: str = "广州新华学院") -> bool:
        """🔥 新增：测试联网搜索能力 🔥"""
        print(f"🧪 测试腾讯云DeepSeek联网搜索能力...")
        
        try:
            test_messages = [
                {
                    "role": "user", 
                    "content": f"请搜索{university}的ESI前1%学科数量，要求使用最新数据"
                }
            ]
            
            completion = self.client.chat.completions.create(
                model="deepseek-v3",
                messages=test_messages,
                temperature=0.1,
                max_tokens=400,
                extra_body={
                    "enable_search": True
                }
            )
            
            response = completion.choices[0].message.content
            print(f"✅ 联网搜索测试成功!")
            print(f"📄 响应长度: {len(response)} 字符")
            
            # 检查是否包含搜索特征
            search_indicators = ["搜索", "查找", "根据", "显示", "数据显示"]
            has_search = any(indicator in response for indicator in search_indicators)
            
            print(f"🔍 包含搜索特征: {'✅' if has_search else '❌'}")
            
            if has_search:
                print(f"🤖 测试回答摘要: {response[:200]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ 联网搜索测试失败: {e}")
            return False

    # =============================================================================
    # 🔥 批量搜索方法 🔥
    # =============================================================================
    
    def search_all_universities_single_metric(self, config_name: str, universities: List[str] = None) -> Dict[str, Any]:
        """搜索所有大学的单个指标"""
        if universities is None:
            universities = self.education_manager.universities
        
        print(f"\n🚀 开始搜索所有大学的 {config_name} 指标")
        print(f"📊 共需搜索 {len(universities)} 所大学")
        
        all_results = []
        start_time = time.time()
        
        for i, university in enumerate(universities, 1):
            print(f"\n[{i}/{len(universities)}] 🔍 搜索 {university}")
            
            result = self.search_single_university_metric(config_name, university)
            all_results.append(result)
            
            # 简单休息
            if i < len(universities):
                time.sleep(random.uniform(2, 5))
        
        # 生成汇总
        summary = self._create_summary(config_name, all_results)
        self._save_results(config_name, summary)
        
        total_time = time.time() - start_time
        print(f"\n🎉 搜索完成! 总耗时: {total_time/60:.1f} 分钟")
        self._print_summary(summary)
        
        return summary
    
    def _create_summary(self, config_name: str, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """创建结果汇总 - 简化版"""
        successful_results = [r for r in all_results if "error" not in r]
        failed_results = [r for r in all_results if "error" in r]
        manual_review_needed = [r for r in successful_results if r.get("requires_manual_review", False)]
        
        # 统计原始回答信息
        total_response_length = sum(r.get("response_length", 0) for r in successful_results)
        complete_responses = len([r for r in successful_results if r.get("is_response_complete", True)])
        
        return {
            "metric": config_name,
            "target_year": self.target_year,
            "search_completed_at": datetime.now().isoformat(),
            "total_universities": len(all_results),
            "successful_searches": len(successful_results),
            "failed_searches": len(failed_results),
            "manual_review_required": len(manual_review_needed),
            "success_rate": f"{(len(successful_results)/len(all_results)*100):.1f}%" if all_results else "0%",
            
            # 原始回答统计
            "response_statistics": {
                "total_response_length": total_response_length,
                "average_response_length": total_response_length // len(successful_results) if successful_results else 0,
                "complete_responses": complete_responses,
                "truncated_responses": len(successful_results) - complete_responses
            },
            
            # 🔥 大学数据 🔥
            "university_data": {
                result["university"]: {
                    "data_value": result.get("data_value", "无数据"),
                    "name_verification": result.get("name_verification", False),
                    "official_source_verified": result.get("official_source_verified", False),
                    "data_quality": result.get("data_quality", "未知"),
                    "requires_manual_review": result.get("requires_manual_review", False),
                    "llm_raw_response": result.get("llm_raw_response", ""),
                    "response_length": result.get("response_length", 0),
                    "is_response_complete": result.get("is_response_complete", True),
                    "data_sources": result.get("data_sources", [])
                }
                for result in successful_results
            },
            
            "failed_universities": [
                {"university": r["university"], "error": r.get("error", "未知错误")}
                for r in failed_results
            ]
        }
    
    def _print_summary(self, summary: Dict[str, Any]):
        """打印摘要 - 简化版"""
        response_stats = summary.get("response_statistics", {})
        
        print(f"\n📈 搜索摘要:")
        print(f"   📊 总搜索: {summary['total_universities']} 所大学")
        print(f"   ✅ 成功: {summary['successful_searches']} 所 ({summary['success_rate']})")
        print(f"   ❌ 失败: {summary['failed_searches']} 所")
        print(f"   ⚠️  需人工核查: {summary['manual_review_required']} 所")
        
        # 显示回答统计
        print(f"   📄 总回答长度: {response_stats.get('total_response_length', 0):,} 字符")
        print(f"   📊 平均回答长度: {response_stats.get('average_response_length', 0):,} 字符")
        print(f"   ✅ 完整回答: {response_stats.get('complete_responses', 0)} 个")
        
        truncated = response_stats.get('truncated_responses', 0)
        if truncated > 0:
            print(f"   ⚠️  可能截断: {truncated} 个")
    
    def _save_results(self, config_name: str, summary: Dict[str, Any]):
        """保存结果"""
        os.makedirs(self.base_output_dir, exist_ok=True)
        
        filename = f"{config_name}_{self.target_year}_deepseek.json"
        filepath = os.path.join(self.base_output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            print(f"\n💾 结果已保存: {filepath}")
        except Exception as e:
            print(f"❌ 保存失败: {e}")

    # =============================================================================
    # 🔥 便捷方法 🔥
    # =============================================================================
    
    def list_available_configs(self) -> List[str]:
        """列出可用配置"""
        return list(self.education_manager.list_configs().keys())
    
    def list_available_universities(self) -> List[str]:
        """列出可用大学"""
        return self.education_manager.universities
    
    def search_single_university_all_metrics(self, university: str) -> Dict[str, Any]:
        """搜索单个大学的所有指标"""
        configs = self.list_available_configs()
        results = {}
        
        for config_name in configs:
            print(f"\n📋 搜索 {university} - {config_name}")
            result = self.search_single_university_metric(config_name, university)
            results[config_name] = result
            time.sleep(random.uniform(3, 6))
        
        return {
            "university": university,
            "target_year": self.target_year,
            "metrics": results,
            "search_completed_at": datetime.now().isoformat()
        }

    # =============================================================================
    # 🔥 原始回答导出和查看方法 🔥
    # =============================================================================
    
    def export_raw_responses_to_txt(self, result_file_path: str, output_txt_path: str = None) -> str:
        """🔥 导出原始LLM回答到文本文件 🔥"""
        if output_txt_path is None:
            base_name = os.path.splitext(os.path.basename(result_file_path))[0]
            output_txt_path = os.path.join(
                os.path.dirname(result_file_path), 
                f"{base_name}_raw_responses.txt"
            )
        
        try:
            # 读取JSON结果
            with open(result_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 提取大学数据
            university_data = data.get("university_data", {})
            metric = data.get("metric", "unknown_metric")
            target_year = data.get("target_year", "unknown_year")
            
            # 写入文本文件
            with open(output_txt_path, 'w', encoding='utf-8') as f:
                f.write(f"=" * 80 + "\n")
                f.write(f"LLM原始回答导出 - {metric} ({target_year}年)\n")
                f.write(f"导出时间: {datetime.now().isoformat()}\n")
                f.write(f"总计: {len(university_data)} 所大学\n")
                f.write(f"搜索引擎: 腾讯云DeepSeek联网搜索\n")
                f.write(f"=" * 80 + "\n\n")
                
                for i, (university, info) in enumerate(university_data.items(), 1):
                    f.write(f"[{i:02d}] {university}\n")
                    f.write(f"{'=' * 50}\n")
                    f.write(f"数据值: {info.get('data_value', '无数据')}\n")
                    f.write(f"回答长度: {info.get('response_length', 0)} 字符\n")
                    f.write(f"完整性: {'✅ 完整' if info.get('is_response_complete', True) else '⚠️ 可能截断'}\n")
                    f.write(f"数据源: {', '.join(info.get('data_sources', []))}\n")
                    f.write(f"-" * 50 + "\n")
                    
                    # 🔥 完整的LLM原始回答 🔥
                    raw_response = info.get('llm_raw_response', '无回答')
                    f.write(f"LLM原始回答:\n{raw_response}\n")
                    
                    f.write(f"\n" + "=" * 80 + "\n\n")
            
            print(f"💾 原始回答已导出: {output_txt_path}")
            return output_txt_path
            
        except Exception as e:
            print(f"❌ 导出原始回答失败: {e}")
            raise e

    def get_single_university_raw_response(self, result_file_path: str, university_name: str) -> str:
        """🔥 获取单个大学的原始回答 🔥"""
        try:
            with open(result_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            university_data = data.get("university_data", {})
            if university_name in university_data:
                info = university_data[university_name]
                raw_response = info.get('llm_raw_response', '')
                
                print(f"📄 {university_name} 的原始回答 ({len(raw_response)} 字符):")
                print("-" * 50)
                print(raw_response)
                print("-" * 50)
                
                return raw_response
            else:
                print(f"❌ 未找到 {university_name} 的数据")
                return ""
                
        except Exception as e:
            print(f"❌ 读取失败: {e}")
            return ""

    def show_response_summary(self, result_file_path: str):
        """🔥 显示回答概要统计 🔥"""
        try:
            with open(result_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            university_data = data.get("university_data", {})
            response_stats = data.get("response_statistics", {})
            
            print(f"\n📊 回答统计摘要:")
            print(f"   📄 总回答长度: {response_stats.get('total_response_length', 0):,} 字符")
            print(f"   📊 平均回答长度: {response_stats.get('average_response_length', 0):,} 字符")
            print(f"   ✅ 完整回答: {response_stats.get('complete_responses', 0)} 个")
            print(f"   ⚠️  可能截断: {response_stats.get('truncated_responses', 0)} 个")
            
            print(f"\n📋 大学回答长度排行:")
            # 按回答长度排序
            universities_by_length = sorted(
                university_data.items(), 
                key=lambda x: x[1].get('response_length', 0), 
                reverse=True
            )
            
            for i, (university, info) in enumerate(universities_by_length[:10], 1):
                length = info.get('response_length', 0)
                complete = '✅' if info.get('is_response_complete', True) else '⚠️'
                print(f"   {i:2d}. {university}: {length:,} 字符 {complete}")
                
        except Exception as e:
            print(f"❌ 显示统计失败: {e}")
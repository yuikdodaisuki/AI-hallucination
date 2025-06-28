"""
教育数据核验程序 - 专注于大模型原始回答质量核验
使用联网搜索核验LLM原始回答的准确性和完整性
"""

import os
import json
import glob
import time
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from openai import OpenAI, APIConnectionError, APIError, RateLimitError
from dataclasses import dataclass

# =============================================================================
# 🔥 配置信息 🔥
# =============================================================================

VERIFICATION_CONFIG = {
    "api_key": "sk-24XB4aUrtxi5iGUIUwHDLsgkst4sy47hKHy4j9Mg97gLG1sC",
    "base_url": "https://api.lkeap.cloud.tencent.com/v1",
    "model": "deepseek-r1",
    "data_folder": "./data",  # JSON文件所在文件夹
    "output_folder": "./verification_reports",  # 核验报告输出文件夹
    "batch_size": 3,  # 批量处理大小（减小以便更仔细核验）
    "delay_between_requests": (5, 10)  # 请求间隔（秒）
}

# =============================================================================
# 🔥 数据模型 🔥
# =============================================================================

@dataclass
class ResponseVerificationResult:
    """LLM回答核验结果数据类"""
    university: str
    metric: str
    original_response: str
    response_length: int
    
    # 回答质量评估
    information_completeness: str  # 信息完整性：完整/部分完整/不完整
    factual_accuracy: str         # 事实准确性：准确/部分准确/不准确
    source_reliability: str       # 数据源可靠性：可靠/一般/不可靠
    response_relevance: str       # 回答相关性：高度相关/相关/不相关
    
    # 具体问题识别
    identified_issues: List[str]   # 发现的具体问题
    missing_information: List[str] # 缺失的信息
    contradictory_info: List[str]  # 矛盾信息
    outdated_info: List[str]       # 过时信息
    
    # 网络核验结果
    web_verification_summary: str  # 网络核验总结
    authoritative_sources: List[str] # 权威数据源
    verified_facts: List[str]      # 核验确认的事实
    disputed_facts: List[str]      # 有争议的事实
    
    # 综合评估
    overall_quality_score: int     # 综合质量评分 (0-100)
    credibility_rating: str        # 可信度评级：高/中/低
    requires_correction: bool      # 是否需要纠正
    
    # 原始数据
    verification_details: str      # 详细核验说明
    raw_verification_response: str # 原始核验回答
    timestamp: str

# =============================================================================
# 🔥 LLM回答质量核验器 🔥
# =============================================================================

class LLMResponseVerifier:
    """LLM回答质量核验器"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=VERIFICATION_CONFIG["api_key"],
            base_url=VERIFICATION_CONFIG["base_url"]
        )
        
        # 确保输出文件夹存在
        os.makedirs(VERIFICATION_CONFIG["output_folder"], exist_ok=True)
        
        # 指标描述映射
        self.metric_descriptions = {
            "esi_1_percent": "ESI前1%学科数量",
            "esi_1_permille": "ESI前1‰学科数量", 
            "undergraduate_majors_total": "本科专业总数",
            "major_accreditation": "专业认证通过数量",
            "national_first_class_majors": "国家级一流本科专业建设点数量",
            "provincial_first_class_majors": "省级一流本科专业建设点数量",
            "national_teaching_awards": "国家级教学成果奖数量",
            "provincial_teaching_awards": "省级教学成果奖数量",
            "youth_teacher_competition": "全国高校青年教师教学竞赛获奖数量",
            "national_first_class_courses": "国家级一流本科课程数量",
            "provincial_first_class_courses": "省级一流本科课程数量",
            "national_smart_platform_courses": "国家智慧教育平台课程数量",
            "provincial_smart_platform_courses": "省级智慧教育平台课程数量"
        }

    def load_data_files(self) -> List[Dict[str, Any]]:
        """加载data文件夹中的所有JSON文件"""
        data_files = []
        json_pattern = os.path.join(VERIFICATION_CONFIG["data_folder"], "*.json")
        
        for file_path in glob.glob(json_pattern):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data_files.append({
                        "file_path": file_path,
                        "file_name": os.path.basename(file_path),
                        "data": data
                    })
                    print(f"✅ 已加载: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"❌ 加载失败 {file_path}: {e}")
        
        print(f"\n📁 总共加载了 {len(data_files)} 个数据文件")
        return data_files

    def create_response_verification_prompt(self, university: str, metric: str, original_response: str, year: int = 2024) -> str:
        """创建LLM回答质量核验提示词"""
        metric_description = self.metric_descriptions.get(metric, metric)
        
        # 截取回答的前1000字符用于展示（避免提示词过长）
        response_preview = original_response[:1000] + "..." if len(original_response) > 1000 else original_response
        
        return f"""请对以下LLM原始回答进行全面质量核验：

🎯 **核验目标**：
- **学校名称**: {university}
- **查询指标**: {metric_description}
- **目标年份**: {year}年

📋 **原始LLM回答**：
{response_preview}

🔍 **核验维度和要求**：

1️⃣ **信息完整性核验**：
   - 回答是否包含了查询指标的完整信息？
   - 是否提供了具体的数量、名称、时间等关键信息？
   - 缺失哪些重要信息？

2️⃣ **事实准确性核验**：
   - 请联网搜索验证回答中的关键事实
   - 学校名称是否正确？是否存在混淆？
   - 数据是否与权威源一致？
   - 时间信息是否准确？

3️⃣ **数据源可靠性核验**：
   - 回答中提到的数据源是否权威？
   - 是否引用了官方网站、政府部门等可信源？
   - 数据源的时效性如何？

4️⃣ **逻辑一致性核验**：
   - 回答内部是否存在矛盾信息？
   - 数据前后是否一致？
   - 推理逻辑是否合理？

5️⃣ **时效性核验**：
   - 数据是否为{year}年的最新信息？
   - 是否使用了过时的数据？
   - 时间标注是否明确？

🏛️ **权威数据源对比**：
请联网搜索以下权威源进行对比验证：
- {university}官网
- 教育部官网 (moe.gov.cn)
- 省教育厅官网
- 权威教育媒体
- 专业认证机构官网

📊 **核验输出格式**：

**信息完整性**: [完整/部分完整/不完整]
**事实准确性**: [准确/部分准确/不准确]
**数据源可靠性**: [可靠/一般/不可靠]
**回答相关性**: [高度相关/相关/不相关]

**发现的问题**:
- 问题1: [具体描述]
- 问题2: [具体描述]

**缺失信息**:
- 缺失1: [具体描述]
- 缺失2: [具体描述]

**网络核验结果**:
- 核验确认的事实: [列出经过核验确认的内容]
- 有争议的事实: [列出存在争议或不一致的内容]
- 权威数据源: [列出找到的权威数据源链接]

**综合质量评分**: [0-100分]
**可信度评级**: [高/中/低]
**是否需要纠正**: [是/否]

**详细核验说明**:
[提供详细的核验过程和发现的具体问题]

请开始联网核验..."""

    def verify_single_response(self, university: str, metric: str, original_response: str, year: int = 2024) -> ResponseVerificationResult:
        """核验单个LLM回答"""
        try:
            print(f"🔍 正在核验回答: {university} - {metric}")
            print(f"   回答长度: {len(original_response)} 字符")
            
            # 创建核验提示词
            prompt = self.create_response_verification_prompt(university, metric, original_response, year)
            
            # 调用API进行联网搜索核验
            response = self.client.chat.completions.create(
                model=VERIFICATION_CONFIG["model"],
                messages=[
                    {"role": "system", "content": "你是专业的教育数据质量审查专家，擅长通过联网搜索核验LLM回答的准确性、完整性和可信度。你需要严格、客观地评估回答质量，指出具体问题和改进建议。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,  # 增加回答长度以获得详细核验
                temperature=0.1,
                extra_body={
                    "enable_search": True  # 启用联网搜索
                }
            )
            
            raw_verification_response = response.choices[0].message.content
            
            # 解析核验结果
            verification_result = self._parse_response_verification(
                university, metric, original_response, raw_verification_response
            )
            
            print(f"   ✅ 核验完成: {verification_result.credibility_rating}可信度")
            return verification_result
            
        except Exception as e:
            print(f"   ❌ 核验失败: {str(e)}")
            return ResponseVerificationResult(
                university=university,
                metric=metric,
                original_response=original_response,
                response_length=len(original_response),
                information_completeness="无法评估",
                factual_accuracy="无法评估",
                source_reliability="无法评估",
                response_relevance="无法评估",
                identified_issues=[f"核验失败: {str(e)}"],
                missing_information=[],
                contradictory_info=[],
                outdated_info=[],
                web_verification_summary="核验失败",
                authoritative_sources=[],
                verified_facts=[],
                disputed_facts=[],
                overall_quality_score=0,
                credibility_rating="无法评估",
                requires_correction=True,
                verification_details=f"API调用失败: {str(e)}",
                raw_verification_response="",
                timestamp=datetime.now().isoformat()
            )

    def _parse_response_verification(self, university: str, metric: str, original_response: str, verification_response: str) -> ResponseVerificationResult:
        """解析LLM回答核验结果"""
        import re
        
        # 提取各个维度的评估结果
        def extract_field(pattern, default="未知"):
            match = re.search(pattern, verification_response, re.IGNORECASE)
            return match.group(1).strip() if match else default
        
        # 提取列表信息
        def extract_list(pattern):
            matches = re.findall(pattern, verification_response, re.IGNORECASE | re.MULTILINE)
            return [match.strip() for match in matches if match.strip()]
        
        # 提取评估维度
        information_completeness = extract_field(r'信息完整性[：:]\s*([^\n]+)', "未评估")
        factual_accuracy = extract_field(r'事实准确性[：:]\s*([^\n]+)', "未评估")
        source_reliability = extract_field(r'数据源可靠性[：:]\s*([^\n]+)', "未评估")
        response_relevance = extract_field(r'回答相关性[：:]\s*([^\n]+)', "未评估")
        
        # 提取问题列表
        identified_issues = extract_list(r'问题\d+[：:]\s*([^\n]+)')
        missing_information = extract_list(r'缺失\d+[：:]\s*([^\n]+)')
        
        # 提取矛盾和过时信息
        contradictory_info = []
        outdated_info = []
        if "矛盾" in verification_response:
            contradictory_info = extract_list(r'矛盾.*?[：:]\s*([^\n]+)')
        if "过时" in verification_response:
            outdated_info = extract_list(r'过时.*?[：:]\s*([^\n]+)')
        
        # 提取核验结果
        verified_facts = extract_list(r'核验确认的事实[：:].*?-\s*([^\n]+)')
        disputed_facts = extract_list(r'有争议的事实[：:].*?-\s*([^\n]+)')
        
        # 提取权威数据源
        authoritative_sources = []
        url_patterns = [r'https?://[^\s\)]+', r'[^\s]+\.edu\.cn', r'[^\s]+\.gov\.cn']
        for pattern in url_patterns:
            authoritative_sources.extend(re.findall(pattern, verification_response))
        
        # 提取评分和评级
        score_match = re.search(r'综合质量评分[：:]\s*(\d+)', verification_response)
        overall_quality_score = int(score_match.group(1)) if score_match else 50
        
        credibility_rating = extract_field(r'可信度评级[：:]\s*([^\n]+)', "中")
        
        # 判断是否需要纠正
        requires_correction = "需要纠正" in verification_response and "是" in verification_response
        
        # 提取详细说明
        details_match = re.search(r'详细核验说明[：:]\s*(.*?)(?:\n\n|\Z)', verification_response, re.DOTALL)
        verification_details = details_match.group(1).strip() if details_match else "无详细说明"
        
        # 提取网络核验总结
        web_summary_match = re.search(r'网络核验结果[：:](.*?)(?=\*\*|$)', verification_response, re.DOTALL)
        web_verification_summary = web_summary_match.group(1).strip() if web_summary_match else "无网络核验总结"
        
        return ResponseVerificationResult(
            university=university,
            metric=metric,
            original_response=original_response,
            response_length=len(original_response),
            information_completeness=information_completeness,
            factual_accuracy=factual_accuracy,
            source_reliability=source_reliability,
            response_relevance=response_relevance,
            identified_issues=identified_issues,
            missing_information=missing_information,
            contradictory_info=contradictory_info,
            outdated_info=outdated_info,
            web_verification_summary=web_verification_summary,
            authoritative_sources=list(set(authoritative_sources)),  # 去重
            verified_facts=verified_facts,
            disputed_facts=disputed_facts,
            overall_quality_score=overall_quality_score,
            credibility_rating=credibility_rating,
            requires_correction=requires_correction,
            verification_details=verification_details,
            raw_verification_response=verification_response,
            timestamp=datetime.now().isoformat()
        )

    def verify_data_file(self, data_file: Dict[str, Any]) -> List[ResponseVerificationResult]:
        """核验单个数据文件中的所有LLM回答"""
        results = []
        data = data_file["data"]
        file_name = data_file["file_name"]
        
        print(f"\n📋 开始核验文件: {file_name}")
        
        # 提取基本信息
        metric = data.get("metric", "未知指标")
        target_year = data.get("target_year", 2024)
        university_data = data.get("university_data", {})
        
        print(f"   指标: {metric}")
        print(f"   年份: {target_year}")
        print(f"   学校数量: {len(university_data)}")
        
        # 逐个核验学校的LLM回答
        for i, (university, info) in enumerate(university_data.items(), 1):
            print(f"\n   [{i}/{len(university_data)}] {university}")
            
            # 获取原始LLM回答
            original_response = info.get("llm_raw_response", "")
            
            # 跳过空回答
            if not original_response or original_response.strip() == "":
                print(f"   ⏭️  跳过空回答")
                continue
            
            # 核验单个回答
            result = self.verify_single_response(university, metric, original_response, target_year)
            results.append(result)
            
            # 请求间隔
            if i < len(university_data):
                delay = random.uniform(*VERIFICATION_CONFIG["delay_between_requests"])
                time.sleep(delay)
        
        return results

    def verify_all_responses(self) -> Dict[str, Any]:
        """核验所有数据文件中的LLM回答"""
        print("🚀 开始批量LLM回答质量核验...")
        
        # 加载所有数据文件
        data_files = self.load_data_files()
        
        if not data_files:
            print("❌ 未找到任何数据文件")
            return {}
        
        all_results = []
        start_time = time.time()
        
        # 逐文件核验
        for i, data_file in enumerate(data_files, 1):
            print(f"\n{'='*60}")
            print(f"📁 [{i}/{len(data_files)}] 核验文件: {data_file['file_name']}")
            
            file_results = self.verify_data_file(data_file)
            all_results.extend(file_results)
            
            # 文件间休息
            if i < len(data_files):
                time.sleep(random.uniform(8, 15))
        
        # 生成核验报告
        report = self._generate_verification_report(all_results)
        
        # 保存报告
        self._save_verification_report(report)
        
        total_time = time.time() - start_time
        print(f"\n🎉 回答质量核验完成! 总耗时: {total_time/60:.1f} 分钟")
        self._print_verification_summary(report)
        
        return report

    def _generate_verification_report(self, results: List[ResponseVerificationResult]) -> Dict[str, Any]:
        """生成LLM回答质量核验报告"""
        
        if not results:
            return {
                "summary": {"total": 0, "high_quality": 0, "needs_improvement": 0},
                "details": []
            }
        
        # 统计分析
        total_count = len(results)
        high_quality = len([r for r in results if r.overall_quality_score >= 80])
        medium_quality = len([r for r in results if 60 <= r.overall_quality_score < 80])
        low_quality = len([r for r in results if r.overall_quality_score < 60])
        needs_correction = len([r for r in results if r.requires_correction])
        
        # 平均质量评分
        avg_score = sum(r.overall_quality_score for r in results) / total_count if total_count > 0 else 0
        
        # 可信度分布
        credibility_dist = {}
        for result in results:
            rating = result.credibility_rating
            credibility_dist[rating] = credibility_dist.get(rating, 0) + 1
        
        # 常见问题分析
        all_issues = []
        for result in results:
            all_issues.extend(result.identified_issues)
        
        issue_frequency = {}
        for issue in all_issues:
            # 简化问题分类
            if "学校名称" in issue or "名称错误" in issue:
                key = "学校名称错误"
            elif "数据源" in issue or "来源" in issue:
                key = "数据源问题"
            elif "时间" in issue or "年份" in issue:
                key = "时间信息问题"
            elif "数据" in issue or "数值" in issue:
                key = "数据准确性问题"
            elif "完整" in issue or "缺失" in issue:
                key = "信息完整性问题"
            else:
                key = "其他问题"
            
            issue_frequency[key] = issue_frequency.get(key, 0) + 1
        
        # 按指标分组统计
        metric_quality = {}
        for result in results:
            metric = result.metric
            if metric not in metric_quality:
                metric_quality[metric] = {"count": 0, "total_score": 0, "high_quality": 0}
            metric_quality[metric]["count"] += 1
            metric_quality[metric]["total_score"] += result.overall_quality_score
            if result.overall_quality_score >= 80:
                metric_quality[metric]["high_quality"] += 1
        
        # 计算各指标平均质量
        for metric in metric_quality:
            stats = metric_quality[metric]
            stats["avg_score"] = stats["total_score"] / stats["count"]
            stats["quality_rate"] = f"{(stats['high_quality']/stats['count']*100):.1f}%"
        
        return {
            "verification_completed_at": datetime.now().isoformat(),
            "summary": {
                "total_responses_verified": total_count,
                "average_quality_score": f"{avg_score:.1f}",
                "quality_distribution": {
                    "high_quality_80_plus": high_quality,
                    "medium_quality_60_79": medium_quality,
                    "low_quality_below_60": low_quality
                },
                "credibility_distribution": credibility_dist,
                "responses_needing_correction": needs_correction,
                "correction_rate": f"{(needs_correction/total_count*100):.1f}%" if total_count > 0 else "0%"
            },
            "quality_analysis": {
                "metric_quality_breakdown": metric_quality,
                "common_issues_frequency": issue_frequency,
                "improvement_suggestions": self._generate_improvement_suggestions(results)
            },
            "detailed_results": [
                {
                    "university": r.university,
                    "metric": r.metric,
                    "response_length": r.response_length,
                    "quality_score": r.overall_quality_score,
                    "credibility_rating": r.credibility_rating,
                    "information_completeness": r.information_completeness,
                    "factual_accuracy": r.factual_accuracy,
                    "source_reliability": r.source_reliability,
                    "response_relevance": r.response_relevance,
                    "identified_issues_count": len(r.identified_issues),
                    "missing_information_count": len(r.missing_information),
                    "requires_correction": r.requires_correction,
                    "authoritative_sources_found": len(r.authoritative_sources),
                    "timestamp": r.timestamp
                }
                for r in results
            ],
            "raw_verification_data": [
                {
                    "university": r.university,
                    "metric": r.metric,
                    "original_response": r.original_response,
                    "verification_details": r.verification_details,
                    "identified_issues": r.identified_issues,
                    "missing_information": r.missing_information,
                    "contradictory_info": r.contradictory_info,
                    "outdated_info": r.outdated_info,
                    "verified_facts": r.verified_facts,
                    "disputed_facts": r.disputed_facts,
                    "authoritative_sources": r.authoritative_sources,
                    "raw_verification_response": r.raw_verification_response,
                    "timestamp": r.timestamp
                }
                for r in results
            ]
        }

    def _generate_improvement_suggestions(self, results: List[ResponseVerificationResult]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 分析常见问题并生成建议
        all_issues = []
        for result in results:
            all_issues.extend(result.identified_issues)
        
        if any("学校名称" in issue for issue in all_issues):
            suggestions.append("加强学校名称验证机制，避免混淆不同学校")
        
        if any("数据源" in issue for issue in all_issues):
            suggestions.append("优先使用官方权威数据源，并明确标注数据来源")
        
        if any("时间" in issue for issue in all_issues):
            suggestions.append("强化时间信息的准确性，确保使用最新年份数据")
        
        # 根据质量分布给出建议
        low_quality_count = len([r for r in results if r.overall_quality_score < 60])
        if low_quality_count > len(results) * 0.3:
            suggestions.append("总体回答质量偏低，建议优化提示词和搜索策略")
        
        # 根据完整性问题给出建议
        incomplete_responses = len([r for r in results if "不完整" in r.information_completeness])
        if incomplete_responses > len(results) * 0.2:
            suggestions.append("加强信息完整性要求，确保提供具体的数量、名称、时间等详细信息")
        
        return suggestions

    def _save_verification_report(self, report: Dict[str, Any]) -> str:
        """保存LLM回答质量核验报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(
            VERIFICATION_CONFIG["output_folder"], 
            f"llm_response_quality_report_{timestamp}.json"
        )
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 LLM回答质量核验报告已保存: {report_file}")
        return report_file

    def _print_verification_summary(self, report: Dict[str, Any]):
        """打印LLM回答质量核验摘要"""
        summary = report["summary"]
        quality_analysis = report["quality_analysis"]
        
        print(f"\n{'='*60}")
        print("📊 LLM回答质量核验摘要")
        print(f"{'='*60}")
        print(f"总核验回答数: {summary['total_responses_verified']}")
        print(f"平均质量评分: {summary['average_quality_score']}/100")
        print(f"需要纠正的回答: {summary['responses_needing_correction']} ({summary['correction_rate']})")
        
        print(f"\n质量分布:")
        quality_dist = summary['quality_distribution']
        print(f"  高质量(80+): {quality_dist['high_quality_80_plus']}")
        print(f"  中等质量(60-79): {quality_dist['medium_quality_60_79']}")
        print(f"  低质量(<60): {quality_dist['low_quality_below_60']}")
        
        print(f"\n可信度分布:")
        for rating, count in summary['credibility_distribution'].items():
            print(f"  {rating}: {count}")
        
        print(f"\n常见问题:")
        for issue, freq in quality_analysis['common_issues_frequency'].items():
            print(f"  {issue}: {freq}次")
        
        print(f"\n各指标质量表现:")
        for metric, stats in quality_analysis['metric_quality_breakdown'].items():
            print(f"  {metric}: 平均{stats['avg_score']:.1f}分, 高质量率{stats['quality_rate']}")
        
        print(f"\n改进建议:")
        for i, suggestion in enumerate(quality_analysis['improvement_suggestions'], 1):
            print(f"  {i}. {suggestion}")

def main():
    """主函数"""
    print("🎯 LLM回答质量核验程序启动")
    print("-" * 60)
    
    # 检查数据文件夹
    if not os.path.exists(VERIFICATION_CONFIG["data_folder"]):
        print(f"❌ 数据文件夹不存在: {VERIFICATION_CONFIG['data_folder']}")
        return
    
    try:
        # 创建核验器并开始核验
        verifier = LLMResponseVerifier()
        report = verifier.verify_all_responses()
        
        if report:
            print(f"\n✅ LLM回答质量核验任务完成")
        else:
            print(f"\n❌ LLM回答质量核验任务失败")
            
    except APIConnectionError:
        print("❌ 网络连接失败，请检查网络设置")
    except RateLimitError:
        print("❌ 请求超限，请检查API配额或稍后重试")
    except APIError as e:
        print(f"❌ API错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {str(e)}")

if __name__ == "__main__":
    main()
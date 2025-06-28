"""
教育数据搜索主程序 - 腾讯云DeepSeek联网搜索版本
"""
import os
from openai import OpenAI
from education_search_configs import education_manager
from education_searcher import EducationDataSearcher
from datetime import datetime

# 🔥 腾讯云DeepSeek配置 🔥
client = OpenAI(
    base_url="https://api.lkeap.cloud.tencent.com/v1",
    api_key="sk-24XB4aUrtxi5iGUIUwHDLsgkst4sy47hKHy4j9Mg97gLG1sC"
)

def find_project_files():
    """找到项目文件路径"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 向上查找项目根目录
    project_root = current_dir
    for _ in range(5):
        csv_path = os.path.join(project_root, "ai_evaluation_dataset_long.csv")
        if os.path.exists(csv_path):
            data_dir = os.path.join(project_root, "src", "data")
            return data_dir, csv_path
        project_root = os.path.dirname(project_root)
    
    # 如果没找到，使用当前目录
    return os.path.join(current_dir, "data"), None

def test_api_connection(searcher: EducationDataSearcher):
    """🔥 新增：测试API连接和联网搜索能力 🔥"""
    print("\n🧪 测试腾讯云DeepSeek API连接...")
    try:
        success = searcher.test_online_search_capability("广州新华学院")
        if success:
            print("✅ API连接正常，联网搜索功能可用")
            return True
        else:
            print("❌ 联网搜索功能异常")
            return False
    except Exception as e:
        print(f"❌ API连接测试失败: {e}")
        return False

def main():
    """主程序 - 增强版"""
    print("🎓 教育数据搜索系统")
    print("🔍 腾讯云DeepSeek联网搜索版本")
    print("=" * 50)
    
    # 🔥 文件路径处理 🔥
    data_dir, csv_path = find_project_files()
    
    if csv_path and os.path.exists(csv_path):
        education_manager.load_universities(csv_path)
        print(f"✅ 加载了 {len(education_manager.universities)} 所大学")
    else:
        print("❌ 未找到大学数据文件，使用默认配置")
        print(f"   查找路径: ai_evaluation_dataset_long.csv")
    
    # 🔥 年份选择 🔥
    target_year = datetime.now().year
    year_input = input(f"📅 目标年份 (默认{target_year}): ").strip()
    if year_input.isdigit():
        target_year = int(year_input)
    
    # 🔥 初始化搜索器 🔥
    searcher = EducationDataSearcher(client, target_year=target_year, base_output_dir=data_dir)
    
    # 🔥 API连接测试 🔥
    if not test_api_connection(searcher):
        print("⚠️  API连接异常，但您可以继续尝试搜索")
        continue_choice = input("是否继续? (y/n): ").strip().lower()
        if continue_choice not in ['y', 'yes', '']:
            print("👋 退出")
            return
    
    # 🔥 增强主菜单 🔥
    while True:
        print(f"\n📋 搜索选项:")
        print("1. 🚀 批量搜索 (所有大学单个指标)")
        print("2. 🔍 单独搜索 (单个大学单个指标)")
        print("3. 📊 单个大学全部指标")
        print("4. 📋 查看列表 (指标/大学)")
        print("5. 📁 结果管理 (查看/导出)")
        print("6. 🧪 测试功能")
        print("7. 👋 退出")
        
        choice = input("选择 (1-7): ").strip()
        
        if choice == "1":
            batch_search(searcher)
        elif choice == "2":
            single_search(searcher)
        elif choice == "3":
            single_university_all_metrics(searcher)
        elif choice == "4":
            show_lists()
        elif choice == "5":
            result_management(searcher)
        elif choice == "6":
            test_functions(searcher)
        elif choice == "7":
            print("👋 退出")
            break
        else:
            print("❌ 无效选择")

def batch_search(searcher: EducationDataSearcher):
    """🔥 增强批量搜索 🔥"""
    configs = searcher.list_available_configs()
    universities = searcher.list_available_universities()
    
    print(f"\n🚀 批量搜索配置")
    print(f"📊 可用指标: {len(configs)} 个")
    print(f"🏫 可用大学: {len(universities)} 所")
    
    # 选择指标
    print(f"\n📊 选择指标:")
    for i, config in enumerate(configs, 1):
        description = education_manager.list_configs().get(config, config)
        print(f"{i:2d}. {config} - {description}")
    
    try:
        index = int(input("选择指标编号: ")) - 1
        if 0 <= index < len(configs):
            config_name = configs[index]
            
            # 🔥 确认搜索 🔥
            print(f"\n🎯 准备搜索:")
            print(f"   📊 指标: {config_name}")
            print(f"   🏫 大学数: {len(universities)} 所")
            print(f"   📅 目标年份: {searcher.target_year}")
            print(f"   ⏱️  预计耗时: {len(universities) * 0.5:.1f} 分钟")
            
            confirm = input("\n确认开始批量搜索? (y/n): ").strip().lower()
            if confirm in ['y', 'yes', '']:
                print(f"\n🚀 开始批量搜索: {config_name}")
                result = searcher.search_all_universities_single_metric(config_name)
                
                # 🔥 详细结果展示 🔥
                print(f"\n🎉 批量搜索完成!")
                print(f"✅ 成功率: {result.get('success_rate', 'N/A')}")
                print(f"📊 成功: {result.get('successful_searches', 0)} 所")
                print(f"❌ 失败: {result.get('failed_searches', 0)} 所")
                print(f"⚠️  需人工核查: {result.get('manual_review_required', 0)} 所")
                
                # 询问是否查看详细结果
                view_details = input("\n查看详细结果? (y/n): ").strip().lower()
                if view_details in ['y', 'yes']:
                    show_batch_results_summary(result)
            else:
                print("❌ 取消搜索")
        else:
            print("❌ 无效编号")
    except ValueError:
        print("❌ 请输入数字")

def single_search(searcher: EducationDataSearcher):
    """🔥 增强单独搜索 🔥"""
    universities = searcher.list_available_universities()
    configs = searcher.list_available_configs()
    
    # 🔥 改进大学选择 🔥
    print(f"\n🏫 选择大学 (共{len(universities)}所):")
    print("1. 输入大学名称")
    print("2. 从列表选择")
    
    input_method = input("选择方式 (1-2): ").strip()
    
    university = None
    if input_method == "1":
        university_input = input("大学名称: ").strip()
        # 模糊匹配
        matches = [u for u in universities if university_input in u]
        if not matches:
            print("❌ 未找到匹配的大学")
            return
        elif len(matches) == 1:
            university = matches[0]
        else:
            print("🔍 找到多个匹配:")
            for i, match in enumerate(matches[:10], 1):
                print(f"{i}. {match}")
            try:
                choice_idx = int(input("选择编号: ")) - 1
                if 0 <= choice_idx < len(matches):
                    university = matches[choice_idx]
                else:
                    print("❌ 无效编号")
                    return
            except ValueError:
                print("❌ 请输入数字")
                return
    
    elif input_method == "2":
        print("🏫 大学列表 (输入编号):")
        for i, uni in enumerate(universities[:20], 1):
            print(f"{i:2d}. {uni}")
        if len(universities) > 20:
            print("... (仅显示前20所)")
        
        try:
            uni_idx = int(input("大学编号: ")) - 1
            if 0 <= uni_idx < len(universities):
                university = universities[uni_idx]
            else:
                print("❌ 无效编号")
                return
        except ValueError:
            print("❌ 请输入数字")
            return
    
    if not university:
        print("❌ 未选择大学")
        return
    
    # 选择指标
    print(f"\n📊 选择指标 (共{len(configs)}个):")
    for i, config in enumerate(configs, 1):
        description = education_manager.list_configs().get(config, config)
        print(f"{i:2d}. {config} - {description}")
    
    try:
        index = int(input("指标编号: ")) - 1
        if 0 <= index < len(configs):
            config_name = configs[index]
            
            print(f"\n🔍 开始搜索:")
            print(f"   🏫 大学: {university}")
            print(f"   📊 指标: {config_name}")
            print(f"   📅 年份: {searcher.target_year}")
            
            result = searcher.search_single_university_metric(config_name, university)
            
            # 🔥 详细结果显示 🔥
            print(f"\n📊 搜索结果:")
            print(f"   🔢 数据值: {result.get('data_value', '未知')}")
            print(f"   📈 质量评分: {result.get('data_quality', '未知')}")
            print(f"   ✅ 学校验证: {'通过' if result.get('name_verification') else '失败'}")
            print(f"   🏛️ 官网验证: {'通过' if result.get('official_source_verified') else '失败'}")
            print(f"   ⚠️  需人工核查: {'是' if result.get('requires_manual_review') else '否'}")
            print(f"   📄 回答长度: {result.get('response_length', 0)} 字符")
            
            # 询问是否查看原始回答
            view_raw = input("\n查看原始LLM回答? (y/n): ").strip().lower()
            if view_raw in ['y', 'yes']:
                raw_response = result.get('llm_raw_response', '无回答')
                print(f"\n{'='*60}")
                print(f"LLM原始回答:")
                print(f"{'='*60}")
                print(raw_response)
                print(f"{'='*60}")
        else:
            print("❌ 无效编号")
    except ValueError:
        print("❌ 请输入数字")

def single_university_all_metrics(searcher: EducationDataSearcher):
    """🔥 新增：单个大学全部指标搜索 🔥"""
    universities = searcher.list_available_universities()
    configs = searcher.list_available_configs()
    
    print(f"\n🏫 选择大学 (共{len(universities)}所):")
    university_input = input("大学名称: ").strip()
    
    # 模糊匹配
    matches = [u for u in universities if university_input in u]
    if not matches:
        print("❌ 未找到匹配的大学")
        return
    elif len(matches) > 1:
        print("🔍 找到多个匹配:")
        for i, match in enumerate(matches[:5], 1):
            print(f"{i}. {match}")
        try:
            choice_idx = int(input("选择编号: ")) - 1
            university = matches[choice_idx]
        except (ValueError, IndexError):
            print("❌ 无效选择")
            return
    else:
        university = matches[0]
    
    print(f"\n🎯 准备搜索 {university} 的所有指标:")
    print(f"   📊 指标数量: {len(configs)} 个")
    print(f"   ⏱️  预计耗时: {len(configs) * 0.5:.1f} 分钟")
    
    confirm = input("\n确认开始? (y/n): ").strip().lower()
    if confirm in ['y', 'yes', '']:
        result = searcher.search_single_university_all_metrics(university)
        
        print(f"\n🎉 {university} 全指标搜索完成!")
        
        # 显示结果汇总
        metrics_results = result.get('metrics', {})
        success_count = len([r for r in metrics_results.values() if 'error' not in r])
        
        print(f"✅ 成功搜索: {success_count}/{len(configs)} 个指标")
        
        # 显示数据值
        print(f"\n📊 数据汇总:")
        for config_name, metric_result in metrics_results.items():
            data_value = metric_result.get('data_value', '错误')
            status = '✅' if 'error' not in metric_result else '❌'
            print(f"   {status} {config_name}: {data_value}")

def show_lists():
    """🔥 增强列表显示 🔥"""
    print("\n📋 列表选项:")
    print("1. 📊 指标列表")
    print("2. 🏫 大学列表")
    print("3. 📁 已有结果文件")
    
    choice = input("选择 (1-3): ").strip()
    
    if choice == "1":
        configs = education_manager.list_configs()
        print(f"\n📊 指标列表 (共{len(configs)}个):")
        for i, (name, desc) in enumerate(configs.items(), 1):
            print(f"{i:2d}. {name}")
            print(f"     📝 {desc}")
    
    elif choice == "2":
        universities = education_manager.universities
        print(f"\n🏫 大学列表 (共{len(universities)}所):")
        # 🔥 改进分页显示 🔥
        page_size = 15
        total_pages = (len(universities) + page_size - 1) // page_size
        current_page = 1
        
        while current_page <= total_pages:
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, len(universities))
            page_unis = universities[start_idx:end_idx]
            
            print(f"\n📄 第{current_page}/{total_pages}页:")
            for i, uni in enumerate(page_unis, start_idx + 1):
                print(f"{i:3d}. {uni}")
            
            if current_page < total_pages:
                action = input(f"\n操作: (n)下页 (p)上页 (q)退出: ").strip().lower()
                if action == 'n':
                    current_page += 1
                elif action == 'p' and current_page > 1:
                    current_page -= 1
                elif action == 'q':
                    break
            else:
                input("\n已是最后一页，按回车返回...")
                break
    
    elif choice == "3":
        show_result_files()

def show_result_files():
    """🔥 新增：显示已有结果文件 🔥"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(current_dir, "education_search_results")
    
    if not os.path.exists(results_dir):
        print("📁 还没有结果文件")
        return
    
    json_files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
    
    if not json_files:
        print("📁 结果目录为空")
        return
    
    print(f"\n📁 结果文件 (共{len(json_files)}个):")
    for i, filename in enumerate(json_files, 1):
        # 解析文件名
        parts = filename.replace('.json', '').split('_')
        if len(parts) >= 3:
            metric = parts[0]
            year = parts[1]
            model = parts[2]
            file_path = os.path.join(results_dir, filename)
            file_size = os.path.getsize(file_path) / 1024  # KB
            print(f"{i:2d}. {metric} ({year}年) - {model} [{file_size:.1f}KB]")
        else:
            print(f"{i:2d}. {filename}")

def result_management(searcher: EducationDataSearcher):
    """🔥 新增：结果管理功能 🔥"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(current_dir, "education_search_results")
    
    if not os.path.exists(results_dir):
        print("📁 还没有结果文件")
        return
    
    json_files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
    
    if not json_files:
        print("📁 结果目录为空")
        return
    
    print(f"\n📁 结果文件管理 (共{len(json_files)}个):")
    for i, filename in enumerate(json_files, 1):
        print(f"{i:2d}. {filename}")
    
    print(f"\n📋 操作选项:")
    print("1. 📊 查看结果统计")
    print("2. 📄 导出原始回答")
    print("3. 🔍 查看单个大学回答")
    
    action = input("选择操作 (1-3): ").strip()
    
    try:
        file_idx = int(input("选择文件编号: ")) - 1
        if 0 <= file_idx < len(json_files):
            selected_file = json_files[file_idx]
            file_path = os.path.join(results_dir, selected_file)
            
            if action == "1":
                searcher.show_response_summary(file_path)
            elif action == "2":
                output_path = searcher.export_raw_responses_to_txt(file_path)
                print(f"✅ 原始回答已导出到: {output_path}")
            elif action == "3":
                university = input("输入大学名称: ").strip()
                searcher.get_single_university_raw_response(file_path, university)
        else:
            print("❌ 无效文件编号")
    except ValueError:
        print("❌ 请输入数字")

def test_functions(searcher: EducationDataSearcher):
    """🔥 新增：测试功能 🔥"""
    print(f"\n🧪 测试功能:")
    print("1. 🔗 API连接测试")
    print("2. 🔍 联网搜索测试")
    print("3. 📊 配置信息检查")
    
    choice = input("选择测试 (1-3): ").strip()
    
    if choice == "1":
        test_api_connection(searcher)
    elif choice == "2":
        test_university = input("测试大学名称 (默认:广州新华学院): ").strip()
        if not test_university:
            test_university = "广州新华学院"
        searcher.test_online_search_capability(test_university)
    elif choice == "3":
        print(f"\n📊 配置信息:")
        print(f"   🏫 大学数量: {len(searcher.list_available_universities())}")
        print(f"   📊 指标数量: {len(searcher.list_available_configs())}")
        print(f"   📅 目标年份: {searcher.target_year}")
        print(f"   📁 输出目录: {searcher.base_output_dir}")
        print(f"   ⏱️  请求间隔: {searcher.request_interval:.1f}秒")

def show_batch_results_summary(result: dict):
    """🔥 新增：显示批量搜索结果摘要 🔥"""
    university_data = result.get("university_data", {})
    
    print(f"\n📊 详细结果摘要:")
    
    # 按质量分类
    high_quality = []
    medium_quality = []
    low_quality = []
    need_review = []
    
    for uni, data in university_data.items():
        quality_str = data.get("data_quality", "质量得分:0/100")
        score = int(quality_str.split(":")[1].split("/")[0]) if ":" in quality_str else 0
        
        if data.get("requires_manual_review"):
            need_review.append((uni, data.get("data_value", "无数据")))
        elif score >= 80:
            high_quality.append((uni, data.get("data_value", "无数据")))
        elif score >= 60:
            medium_quality.append((uni, data.get("data_value", "无数据")))
        else:
            low_quality.append((uni, data.get("data_value", "无数据")))
    
    if high_quality:
        print(f"\n✅ 高质量结果 ({len(high_quality)}所):")
        for uni, value in high_quality[:5]:
            print(f"   {uni}: {value}")
        if len(high_quality) > 5:
            print(f"   ... 还有{len(high_quality)-5}所")
    
    if medium_quality:
        print(f"\n🟡 中等质量结果 ({len(medium_quality)}所):")
        for uni, value in medium_quality[:3]:
            print(f"   {uni}: {value}")
        if len(medium_quality) > 3:
            print(f"   ... 还有{len(medium_quality)-3}所")
    
    if need_review:
        print(f"\n⚠️  需人工核查 ({len(need_review)}所):")
        for uni, value in need_review[:3]:
            print(f"   {uni}: {value}")
        if len(need_review) > 3:
            print(f"   ... 还有{len(need_review)-3}所")

if __name__ == "__main__":
    main()
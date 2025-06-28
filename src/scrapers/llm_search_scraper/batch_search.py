"""
批量搜索脚本 - 自动搜索所有指标
"""
import time
import os
from datetime import datetime  # 🔥 添加这行导入 🔥
from openai import OpenAI
from education_search_configs import education_manager
from education_searcher import EducationDataSearcher

# 🔥 添加项目根目录查找函数 🔥
def get_project_root():
    """获取项目根目录路径"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = current_dir
    for _ in range(5):
        if os.path.exists(os.path.join(project_root, "ai_evaluation_dataset_long.csv")):
            return project_root
        project_root = os.path.dirname(project_root)
    return None

client = OpenAI(
    base_url="https://api.moonshot.cn/v1",
    api_key="sk-GvZqsEKUs6OIFg346ofcaHMCZRNFFlDl29xVKb8bqXujDg5r"
)

def batch_search_all(target_year: int = None):
    """批量搜索所有指标"""
    if target_year is None:
        target_year = datetime.now().year
    
    # 🔥 获取正确的CSV文件路径和data目录 🔥
    project_root = get_project_root()
    if project_root:
        data_dir = os.path.join(project_root, "src", "data")
        csv_path = os.path.join(project_root, "ai_evaluation_dataset_long.csv")
        print(f"📍 项目根目录: {project_root}")
        print(f"📁 数据输出目录: {data_dir}")
        print(f"📄 CSV文件路径: {csv_path}")
    else:
        print("❌ 无法找到项目根目录")
        return
    
    # 🔥 使用data目录作为基础输出目录初始化搜索器 🔥
    searcher = EducationDataSearcher(client, base_output_dir=data_dir, target_year=target_year)
    
    # 🔥 获取正确的CSV文件路径 🔥
    project_root = get_project_root()
    if project_root:
        csv_path = os.path.join(project_root, "ai_evaluation_dataset_long.csv")
        print(f"📍 项目根目录: {project_root}")
        print(f"📄 CSV文件路径: {csv_path}")
    else:
        print("❌ 无法找到项目根目录")
        return
    
    if os.path.exists(csv_path):
        education_manager.load_universities(csv_path)
    else:
        print(f"❌ 找不到CSV文件: {csv_path}")
        return
    
    configs = education_manager.list_configs()
    universities = education_manager.universities
    
    print("🚀 开始批量搜索")
    print(f"📅 目标年份: {target_year}")
    print(f"📊 指标数量: {len(configs)}")
    print(f"🏫 大学数量: {len(universities)}")
    print("="*60)
    
    for i, (config_name, description) in enumerate(configs.items(), 1):
        print(f"\n[{i}/{len(configs)}] 🔍 搜索指标: {config_name}")
        print(f"描述: {description}")
        
        start_time = time.time()
        # 🔥 现在只返回一个汇总结果 🔥
        result = searcher.search_all_universities_single_metric(config_name)
        end_time = time.time()
        
        print(f"⏱️  耗时: {(end_time - start_time)/60:.1f} 分钟")
        print(f"✅ 完成 {config_name}，成功率: {result.get('success_rate', 'N/A')}")
        
        if i < len(configs):
            print("⏳ 休息 30 秒...")
            time.sleep(30)
    
    print("\n🎉 批量搜索全部完成！")

if __name__ == "__main__":
    import sys
    
    # 🔥 支持命令行年份参数 🔥
    if len(sys.argv) > 1:
        try:
            target_year = int(sys.argv[1])
            batch_search_all(target_year)
        except ValueError:
            print("❌ 年份参数无效，使用当前年份")
            batch_search_all()
    else:
        year = input(f"请输入目标年份 (默认{datetime.now().year}): ").strip()
        if year:
            try:
                batch_search_all(int(year))
            except ValueError:
                print("❌ 年份格式错误，使用当前年份")
                batch_search_all()
        else:
            batch_search_all()
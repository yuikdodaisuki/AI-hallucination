"""
分表格汇总脚本
将多个指标的答案CSV文件汇总成一个总表格
"""

import os
import pandas as pd
import glob
from datetime import datetime
import sys

def find_answer_csv_files(directory="."):
    """
    查找所有符合模式的答案CSV文件
    文件名模式: *_answers.csv
    """
    pattern = os.path.join(directory, "*_answers.csv")
    files = glob.glob(pattern)
    
    # 过滤掉已经是汇总文件的文件
    answer_files = []
    for file in files:
        filename = os.path.basename(file)
        # 排除可能的汇总文件
        if not any(keyword in filename.lower() for keyword in ['merged', 'combined', 'summary', 'all']):
            answer_files.append(file)
    
    return answer_files

def extract_metric_from_filename(filename):
    """
    从文件名中提取指标名称
    例如: ai_evaluation_dataset_long_ESI前1%学科数量_answers.csv -> ESI前1%学科数量
    """
    basename = os.path.basename(filename)
    
    # 移除文件扩展名
    name_without_ext = basename.replace('.csv', '')
    
    # 移除前缀和后缀
    if name_without_ext.startswith('ai_evaluation_dataset_long_'):
        name_without_ext = name_without_ext[len('ai_evaluation_dataset_long_'):]
    
    if name_without_ext.endswith('_answers'):
        name_without_ext = name_without_ext[:-len('_answers')]
    
    return name_without_ext

def read_answer_file(file_path):
    """
    读取答案CSV文件
    返回处理后的数据
    """
    try:
        # 尝试不同的编码方式
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                print(f"  ✅ 使用 {encoding} 编码成功读取: {os.path.basename(file_path)}")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            print(f"  ❌ 无法读取文件 (尝试了所有编码): {file_path}")
            return None
        
        # 检查必需的列
        required_columns = ['学校名称', '指标名称', 'AI答案']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"  ⚠️  文件缺少必需列 {missing_columns}: {file_path}")
            return None
        
        # 只保留需要的列
        df = df[['学校名称', '指标名称', 'AI答案']].copy()
        
        # 清理数据
        df = df.dropna(subset=['学校名称'])  # 删除学校名称为空的行
        df['学校名称'] = df['学校名称'].astype(str).str.strip()
        df['指标名称'] = df['指标名称'].astype(str).str.strip()
        df['AI答案'] = df['AI答案'].astype(str).str.strip()
        
        print(f"  📊 读取到 {len(df)} 条记录")
        return df
        
    except Exception as e:
        print(f"  ❌ 读取文件失败: {file_path}, 错误: {e}")
        return None

def merge_answer_tables(input_directory=".", output_file=None):
    """
    合并所有答案表格
    """
    print("🔍 开始查找答案CSV文件...")
    
    # 查找所有答案文件
    answer_files = find_answer_csv_files(input_directory)
    
    if not answer_files:
        print("❌ 未找到任何答案CSV文件")
        print("💡 请确保文件名格式为: *_answers.csv")
        return False
    
    print(f"📁 找到 {len(answer_files)} 个答案文件:")
    for file in answer_files:
        metric_name = extract_metric_from_filename(file)
        print(f"  📄 {os.path.basename(file)} -> 指标: {metric_name}")
    
    print(f"\n📊 开始读取和合并数据...")
    
    # 存储所有数据
    all_data = []
    successful_files = 0
    
    for file_path in answer_files:
        print(f"\n🔄 处理文件: {os.path.basename(file_path)}")
        
        # 读取文件
        df = read_answer_file(file_path)
        if df is not None and not df.empty:
            all_data.append(df)
            successful_files += 1
        else:
            print(f"  ⚠️  跳过文件: {os.path.basename(file_path)}")
    
    if not all_data:
        print("❌ 没有成功读取任何文件")
        return False
    
    print(f"\n🔗 合并数据...")
    print(f"  成功处理: {successful_files}/{len(answer_files)} 个文件")
    
    # 合并所有数据
    merged_df = pd.concat(all_data, ignore_index=True)
    
    # 数据清理和整理
    print(f"📋 数据整理...")
    
    # 去重（基于学校名称和指标名称）
    before_dedup = len(merged_df)
    merged_df = merged_df.drop_duplicates(subset=['学校名称', '指标名称'], keep='last')
    after_dedup = len(merged_df)
    
    if before_dedup != after_dedup:
        print(f"  🔄 去重: {before_dedup} -> {after_dedup} 条记录")
    
    # 排序
    merged_df = merged_df.sort_values(['学校名称', '指标名称'])
    
    # 添加标准答案列（初始值为"待填充"）
    merged_df.insert(2, '标准答案', '待填充')
    
    # 重新排列列顺序
    merged_df = merged_df[['学校名称', '指标名称', '标准答案', 'AI答案']]
    
    # 统计信息
    unique_schools = merged_df['学校名称'].nunique()
    unique_metrics = merged_df['指标名称'].nunique()
    
    print(f"\n📈 合并结果统计:")
    print(f"  总记录数: {len(merged_df)}")
    print(f"  学校数量: {unique_schools}")
    print(f"  指标数量: {unique_metrics}")
    print(f"  平均每校指标数: {len(merged_df) / unique_schools:.1f}")
    
    # 显示学校列表
    print(f"\n🏫 包含的学校:")
    schools = sorted(merged_df['学校名称'].unique())
    for i, school in enumerate(schools, 1):
        record_count = len(merged_df[merged_df['学校名称'] == school])
        print(f"  {i:2d}. {school} ({record_count} 条记录)")
    
    # 显示指标列表
    print(f"\n📊 包含的指标:")
    metrics = sorted(merged_df['指标名称'].unique())
    for i, metric in enumerate(metrics, 1):
        record_count = len(merged_df[merged_df['指标名称'] == metric])
        print(f"  {i:2d}. {metric} ({record_count} 条记录)")
    
    # 保存结果
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"merged_evaluation_dataset_{timestamp}.csv"
    
    try:
        merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n✅ 合并完成! 结果已保存到: {output_file}")
        
        # 验证保存的文件
        file_size = os.path.getsize(output_file)
        print(f"📁 文件大小: {file_size / 1024:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        return False

def show_file_analysis(directory="."):
    """
    分析目录中的CSV文件
    """
    print("🔍 文件分析报告")
    print("=" * 50)
    
    # 查找所有CSV文件
    all_csv_files = glob.glob(os.path.join(directory, "*.csv"))
    answer_files = find_answer_csv_files(directory)
    
    print(f"📁 目录: {os.path.abspath(directory)}")
    print(f"📄 总CSV文件数: {len(all_csv_files)}")
    print(f"📊 答案文件数: {len(answer_files)}")
    
    if answer_files:
        print(f"\n📋 答案文件详情:")
        for i, file in enumerate(answer_files, 1):
            filename = os.path.basename(file)
            metric = extract_metric_from_filename(file)
            file_size = os.path.getsize(file)
            
            print(f"  {i:2d}. {filename}")
            print(f"      指标: {metric}")
            print(f"      大小: {file_size / 1024:.1f} KB")
            
            # 尝试读取行数
            try:
                df = pd.read_csv(file, encoding='utf-8-sig')
                print(f"      记录: {len(df)} 行")
            except:
                print(f"      记录: 无法读取")
            print()
    
    # 分析非答案文件
    other_files = [f for f in all_csv_files if f not in answer_files]
    if other_files:
        print(f"📋 其他CSV文件:")
        for file in other_files:
            filename = os.path.basename(file)
            file_size = os.path.getsize(file)
            print(f"  • {filename} ({file_size / 1024:.1f} KB)")

def main():
    """主函数"""
    print("🚀 分表格汇总工具")
    print("=" * 50)
    
    # 处理命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command in ['help', '-h', '--help']:
            print("使用说明:")
            print("  python merge_answer_tables.py                    # 合并当前目录的所有答案文件")
            print("  python merge_answer_tables.py analyze            # 分析目录中的CSV文件")
            print("  python merge_answer_tables.py /path/to/directory  # 指定目录进行合并")
            print("  python merge_answer_tables.py help               # 显示此帮助信息")
            return
        
        elif command == 'analyze':
            directory = sys.argv[2] if len(sys.argv) > 2 else "."
            show_file_analysis(directory)
            return
        
        elif os.path.isdir(command):
            # 如果参数是目录路径
            directory = command
            output_file = sys.argv[2] if len(sys.argv) > 2 else None
        else:
            print(f"❌ 无效的命令或路径: {command}")
            return
    else:
        # 默认使用当前目录
        directory = "."
        output_file = None
    
    # 执行合并
    success = merge_answer_tables(directory, output_file)
    
    if success:
        print(f"\n🎉 任务完成!")
    else:
        print(f"\n❌ 任务失败!")

if __name__ == "__main__":
    main()
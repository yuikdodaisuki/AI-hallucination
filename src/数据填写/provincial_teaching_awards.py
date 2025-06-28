#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
填充省级教学成果奖标准答案程序
从省级教学成果奖 JSON文件中提取数据，填充到对应CSV文件的标准答案列中
"""

import json
import pandas as pd
import os
from datetime import datetime
import shutil

def load_school_data(json_file_path):
    """
    从JSON文件中加载学校数据
    
    Args:
        json_file_path (str): JSON文件路径
        
    Returns:
        dict: 包含获奖总数数据的字典，格式为 {学校名: 获奖总数}
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 初始化获奖数据字典
    awards_data = {}
    
    # 提取各学校的获奖总数数据
    for school in data['results']:
        school_name = school['学校名']
        total_awards = school['获奖总数']
        awards_data[school_name] = total_awards
        print(f"{school_name}: {total_awards}")  # 输出学校名称和获奖总数以便调试
    
    return awards_data

def fill_standard_answers(csv_file_path, school_data, output_file_path=None):
    """
    填充CSV文件中的标准答案列
    
    Args:
        csv_file_path (str): 输入CSV文件路径
        school_data (dict): 学校获奖数据映射
        output_file_path (str, optional): 输出文件路径，如果为None则覆盖原文件
    """
    # 读取CSV文件
    df = pd.read_csv(csv_file_path, encoding='utf-8')
    
    # 填充标准答案
    filled_count = 0
    not_found_schools = []
    
    for index, row in df.iterrows():
        school_name = row['学校名称']
        if school_name in school_data:
            df.at[index, '标准答案'] = school_data[school_name]
            filled_count += 1
        else:
            df.at[index, '标准答案'] = '未找到数据'  # 如果未找到学校，则填充为'未找到数据'
            not_found_schools.append(school_name)
    
    # 保存结果
    if output_file_path is None:
        output_file_path = csv_file_path
    
    df.to_csv(output_file_path, index=False, encoding='utf-8')
    
    print(f"省级教学成果奖处理完成!")
    print(f"成功填充 {filled_count} 个学校的标准答案")
    if not_found_schools:
        print(f"未找到匹配的学校 ({len(not_found_schools)} 个): {', '.join(not_found_schools)}")
    print(f"结果已保存到: {output_file_path}")
    
    return df

def process_provincial_teaching_awards(base_dir, json_file, awards_data):
    """
    处理省级教学成果奖数据填充
    
    Args:
        base_dir (str): 基础目录
        json_file (str): JSON文件路径
        awards_data (dict): 获奖数据
    """
    # CSV文件路径
    csv_file = os.path.join(base_dir, 'ai_evaluation_dataset_long_省级教学成果奖_answers.csv')
    
    # 检查CSV文件是否存在
    if not os.path.exists(csv_file):
        print(f"警告: CSV文件不存在: {csv_file}")
        return
    
    try:
        # 创建备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = csv_file.replace('.csv', f'_backup_{timestamp}.csv')
        
        # 备份原文件
        shutil.copy2(csv_file, backup_file)
        print(f"原文件已备份到: {backup_file}")
        
        # 填充标准答案
        print(f"正在填充省级教学成果奖的标准答案...")
        result_df = fill_standard_answers(csv_file, awards_data)
        
        # 显示填充结果预览
        print(f"\n省级教学成果奖填充结果预览:")
        print(result_df[['学校名称', '标准答案', 'AI答案']].head(10).to_string(index=False))
        print("-" * 60)
        
        # 统计匹配情况
        matched_count = len([v for v in result_df['标准答案'] if v != '未找到数据'])
        unmatched_count = len([v for v in result_df['标准答案'] if v == '未找到数据'])
        
        print(f"\n匹配统计:")
        print(f"  成功匹配: {matched_count} 所学校")
        print(f"  未找到数据: {unmatched_count} 所学校")
        
        # 显示未匹配的学校
        if unmatched_count > 0:
            unmatched_schools = result_df[result_df['标准答案'] == '未找到数据']['学校名称'].tolist()
            print(f"\n未找到数据的学校:")
            for school in unmatched_schools:
                print(f"  - {school}")
        
        # 显示获奖数量分布
        award_counts = result_df[result_df['标准答案'] != '未找到数据']['标准答案'].astype(int)
        print(f"\n获奖数量统计:")
        print(f"  平均获奖数: {award_counts.mean():.1f}")
        print(f"  最高获奖数: {award_counts.max()}")
        print(f"  最低获奖数: {award_counts.min()}")
        
    except Exception as e:
        print(f"处理省级教学成果奖时出现错误: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    # 文件路径配置
    # 获取当前脚本所在目录的上级目录（AI-hallucination）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(current_dir))  # 回到AI-hallucination目录
    json_file = os.path.join(base_dir, "src/data/consolidated/省级教学成果奖_data.json")
    
    # 检查JSON文件是否存在
    if not os.path.exists(json_file):
        print(f"错误: JSON文件不存在: {json_file}")
        return
    
    try:
        # 加载学校数据
        print("正在加载省级教学成果奖数据...")
        awards_data = load_school_data(json_file)
        total_schools = len(awards_data)
        print(f"成功加载 {total_schools} 个学校的获奖数据")
        
        # 显示一些示例数据
        print("\n示例数据:")
        for i, (school, awards) in enumerate(list(awards_data.items())[:5]):
            print(f"  {school}: {awards}")
        if total_schools > 5:
            print(f"  ... 还有 {total_schools - 5} 所学校")
        print()
        
        # 显示获奖数量分布概况
        award_values = list(awards_data.values())
        print(f"获奖数量分布:")
        print(f"  平均获奖数: {sum(award_values)/len(award_values):.1f}")
        print(f"  最高获奖数: {max(award_values)} (学校: {[k for k, v in awards_data.items() if v == max(award_values)][0]})")
        print(f"  最低获奖数: {min(award_values)}")
        print()
        
        # 处理数据填充
        process_provincial_teaching_awards(base_dir, json_file, awards_data)
        
        print("=" * 60)
        print("省级教学成果奖数据处理完成！")
        
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

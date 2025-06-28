#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
填充标准答案程序
从school_intro_data JSON文件中提取各种指标数据，填充到对应CSV文件的标准答案列中
支持：本科专业总数、国家级一流本科专业建设点、省级一流本科专业建设点
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
        dict: 包含所有指标数据的字典，格式为 {指标名: {学校名: 数值}}
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 初始化各个指标的数据字典
    indicators_data = {
        '本科专业总数': {},
        '国家级一流本科专业建设点': {},
        '省级一流本科专业建设点': {}
    }
    
    # 提取各学校的数据
    for school in data['schools']:
        school_name = school['school_name']
        indicators_data['本科专业总数'][school_name] = school['undergraduate_majors']
        indicators_data['国家级一流本科专业建设点'][school_name] = school['national_first_class_majors']
        indicators_data['省级一流本科专业建设点'][school_name] = school['provincial_first_class_majors']
    
    return indicators_data

def fill_standard_answers(csv_file_path, school_data_for_indicator, indicator_name, output_file_path=None):
    """
    填充CSV文件中的标准答案列
    
    Args:
        csv_file_path (str): 输入CSV文件路径
        school_data_for_indicator (dict): 特定指标的学校数据映射
        indicator_name (str): 指标名称
        output_file_path (str, optional): 输出文件路径，如果为None则覆盖原文件
    """
    # 读取CSV文件
    df = pd.read_csv(csv_file_path, encoding='utf-8')
    
    # 填充标准答案
    filled_count = 0
    not_found_schools = []
    
    for index, row in df.iterrows():
        school_name = row['学校名称']
        if school_name in school_data_for_indicator:
            df.at[index, '标准答案'] = school_data_for_indicator[school_name]
            filled_count += 1
        else:
            not_found_schools.append(school_name)
    
    # 保存结果
    if output_file_path is None:
        output_file_path = csv_file_path
    
    df.to_csv(output_file_path, index=False, encoding='utf-8')
    
    print(f"指标[{indicator_name}]处理完成!")
    print(f"成功填充 {filled_count} 个学校的标准答案")
    if not_found_schools:
        print(f"未找到匹配的学校 ({len(not_found_schools)} 个): {', '.join(not_found_schools)}")
    print(f"结果已保存到: {output_file_path}")
    
    return df

def process_single_indicator(base_dir, json_file, indicator_name, indicators_data):
    """
    处理单个指标的数据填充
    
    Args:
        base_dir (str): 基础目录
        json_file (str): JSON文件路径
        indicator_name (str): 指标名称
        indicators_data (dict): 所有指标数据
    """
    # 构建CSV文件路径
    csv_file_mapping = {
        '本科专业总数': 'ai_evaluation_dataset_long_本科专业总数_answers.csv',
        '国家级一流本科专业建设点': 'ai_evaluation_dataset_long_国家级一流本科专业建设点_answers.csv',
        '省级一流本科专业建设点': 'ai_evaluation_dataset_long_省级一流本科专业建设点_answers.csv'
    }
    
    if indicator_name not in csv_file_mapping:
        print(f"警告: 未知指标 {indicator_name}")
        return
    
    csv_file = os.path.join(base_dir, csv_file_mapping[indicator_name])
    
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
        print(f"正在填充指标[{indicator_name}]的标准答案...")
        school_data_for_indicator = indicators_data[indicator_name]
        result_df = fill_standard_answers(csv_file, school_data_for_indicator, indicator_name)
        
        # 显示填充结果预览
        print(f"\n指标[{indicator_name}]填充结果预览:")
        print(result_df[['学校名称', '标准答案', 'AI答案']].head(5).to_string(index=False))
        print("-" * 60)
        
    except Exception as e:
        print(f"处理指标[{indicator_name}]时出现错误: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    # 文件路径配置
    base_dir = "/Users/a1/study/爬虫/AI-hallucination"
    json_file = os.path.join(base_dir, "src/data/school_data/school_intro_data_20250615_162208.json")
    
    # 检查JSON文件是否存在
    if not os.path.exists(json_file):
        print(f"错误: JSON文件不存在: {json_file}")
        return
    
    try:
        # 加载学校数据
        print("正在加载学校数据...")
        indicators_data = load_school_data(json_file)
        total_schools = len(indicators_data['本科专业总数'])
        print(f"成功加载 {total_schools} 个学校的数据")
        
        # 要处理的指标列表
        indicators_to_process = [
            '本科专业总数',
            '国家级一流本科专业建设点', 
            '省级一流本科专业建设点'
        ]
        
        print(f"\n准备处理 {len(indicators_to_process)} 个指标:")
        for indicator in indicators_to_process:
            print(f"  - {indicator}")
        print()
        
        # 逐个处理各指标
        for indicator_name in indicators_to_process:
            process_single_indicator(base_dir, json_file, indicator_name, indicators_data)
        
        print("=" * 60)
        print("所有指标处理完成！")
        
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

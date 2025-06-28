#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
去除学科评估数据中的重复项
"""

import json
import os
from datetime import datetime

def remove_duplicates(input_file_path, output_file_path=None):
    """
    去除JSON文件中的重复数据
    
    Args:
        input_file_path (str): 输入文件路径
        output_file_path (str, optional): 输出文件路径，如果为None则覆盖原文件
    """
    print(f"正在读取文件: {input_file_path}")
    
    # 读取原始数据
    with open(input_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"原始数据条目数: {len(data)}")
    print(data[:5])  # 显示前5条数据样本
    # 使用集合来去重，基于(subject_name, school_name, rating)的组合
    unique_items = []
    seen_combinations = set()
    
    for item in data:
        # 创建唯一标识符
        key = (item['subject_name'], item['school_name'], item['rating'])
        
        if key not in seen_combinations:
            seen_combinations.add(key)
            unique_items.append(item)
    
    print(f"去重后数据条目数: {len(unique_items)}")
    print(f"移除了 {len(data) - len(unique_items)} 个重复条目")
    
    # 输出文件路径
    if output_file_path is None:
        # 创建备份
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = input_file_path.replace('.json', f'_backup_{timestamp}.json')
        
        import shutil
        shutil.copy2(input_file_path, backup_file)
        print(f"原文件已备份到: {backup_file}")
        
        output_file_path = input_file_path
    
    # 保存去重后的数据
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(unique_items, f, ensure_ascii=False, indent=2)
    
    print(f"去重后的数据已保存到: {output_file_path}")
    
    # 显示一些样本数据
    print("\n去重后数据样本:")
    for i, item in enumerate(unique_items[:10]):
        print(f"  {i+1}. {item['subject_name']} - {item['school_name']} - {item['rating']}")
    
    return unique_items

def analyze_data_structure(data):
    """
    分析数据结构
    """
    print("\n数据结构分析:")
    
    # 统计学科数量
    subjects = set(item['subject_name'] for item in data)
    print(f"学科总数: {len(subjects)}")
    
    # 统计学校数量
    schools = set(item['school_name'] for item in data)
    print(f"学校总数: {len(schools)}")
    
    # 统计评级分布
    ratings = {}
    for item in data:
        rating = item['rating']
        ratings[rating] = ratings.get(rating, 0) + 1
    
    print("评级分布:")
    for rating in sorted(ratings.keys()):
        print(f"  {rating}: {ratings[rating]} 个")

def main():
    """主函数"""
    input_file = "/Users/a1/study/爬虫/AI-hallucination/src/data/subject_evaluation/subject_evaluation_data.json"
    
    if not os.path.exists(input_file):
        print(f"错误: 文件不存在 {input_file}")
        return
    
    try:
        # 去除重复数据
        unique_data = remove_duplicates(input_file)
        
        # 分析数据结构
        analyze_data_structure(unique_data)
        
        print("\n处理完成！")
        
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

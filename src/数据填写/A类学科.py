#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教育部评估A类学科数量填充程序
从subject_evaluation_data.json文件中统计每个学校的A类学科数量（A+、A、A-），
填充到CSV文件的标准答案列中
"""

import json
import pandas as pd
import os
from datetime import datetime
import shutil

def load_subject_evaluation_data(json_file_path):
    """
    从JSON文件中加载学科评估数据并统计每个学校的A类学科数量
    
    Args:
        json_file_path (str): JSON文件路径
        
    Returns:
        dict: 学校名称到A类学科数量的映射，格式为 {"学校名": A类学科数量}
    """
    # 打开并读取JSON文件
    # 'r' 表示只读模式，encoding='utf-8' 确保正确读取中文
    with open(json_file_path, 'r', encoding='utf-8') as f:
        # json.load() 将JSON文件内容解析为Python对象（通常是list或dict）
        data = json.load(f)
    
    # 初始化字典，用于存储每个学校的A类学科数量
    school_a_subjects = {}
    
    # 定义A类评级包括的等级：A+（最高）、A（高）、A-（较高）
    a_ratings = ['A+', 'A', 'A-']
    
    # 遍历JSON数据中的每一条记录
    # 每条记录包含：学校名称、学科名称、评级等信息
    for item in data:
        school_name = item['school_name']  # 获取学校名称
        rating = item['rating']            # 获取该学科的评级
        
        # 只统计A类学科（A+、A、A-），忽略B类和C类
        if rating in a_ratings:
            # 如果该学校还没有在字典中，初始化为0
            if school_name not in school_a_subjects:
                school_a_subjects[school_name] = 0
            # 该学校的A类学科数量加1
            school_a_subjects[school_name] += 1
    
    return school_a_subjects

def fill_a_subject_counts(csv_file_path, school_a_counts, output_file_path=None):
    """
    填充CSV文件中的教育部评估A类学科数量标准答案列
    
    Args:
        csv_file_path (str): 输入CSV文件路径
        school_a_counts (dict): 学校A类学科数量映射，格式为 {"学校名": A类学科数量}
        output_file_path (str, optional): 输出文件路径，如果为None则覆盖原文件
    """
    # 使用pandas读取CSV文件，返回DataFrame对象
    # encoding='utf-8' 确保能正确读取中文字符
    df = pd.read_csv(csv_file_path, encoding='utf-8')
    
    # 初始化计数器和记录列表
    filled_count = 0          # 记录成功填充的学校数量
    not_found_schools = []    # 记录在JSON数据中未找到的学校
    
    # df.iterrows() 遍历DataFrame的每一行
    # 返回 (索引, 行数据) 的元组，其中行数据是pandas Series对象
    for index, row in df.iterrows():
        # 从当前行的'学校名称'列获取学校名
        # row['学校名称'] 相当于访问Series对象的指定列
        school_name = row['学校名称']
        
        # 检查学校是否在A类学科统计字典中
        if school_name in school_a_counts:
            # df.at[行索引, 列名] 用于设置DataFrame中指定位置的值
            # 将该学校的A类学科数量填入'标准答案'列
            df.at[index, '标准答案'] = school_a_counts[school_name]
            filled_count += 1  # 成功填充计数器加1
        else:
            # 如果学校不在统计中，将标准答案设为0（表示没有A类学科）
            df.at[index, '标准答案'] = 0
            not_found_schools.append(school_name)  # 记录未找到的学校
    
    # 保存修改后的DataFrame到文件
    if output_file_path is None:
        output_file_path = csv_file_path  # 如果没有指定输出路径，覆盖原文件
    
    # 将DataFrame保存为CSV文件
    # index=False 表示不保存行索引到文件中
    # encoding='utf-8' 确保中文字符正确保存
    df.to_csv(output_file_path, index=False, encoding='utf-8')
    
    # 输出处理结果统计信息
    print(f"教育部评估A类学科数量填充完成!")
    print(f"成功填充 {len(df)} 个学校的标准答案")  # len(df) 获取DataFrame的行数
    print(f"其中 {filled_count} 个学校有A类学科")
    
    # 如果有未找到的学校，显示相关信息
    if not_found_schools:
        # 显示前10个未找到的学校名称
        print(f"未在学科评估数据中找到的学校 ({len(not_found_schools)} 个): {', '.join(not_found_schools[:10])}")
        # 如果超过10个，显示还有多少个
        if len(not_found_schools) > 10:
            print(f"... 还有 {len(not_found_schools) - 10} 个学校")
    print(f"结果已保存到: {output_file_path}")
    
    return df  # 返回处理后的DataFrame

def display_statistics(school_a_counts, df):
    """
    显示统计信息和数据分析结果
    
    Args:
        school_a_counts (dict): 学校A类学科数量映射字典
        df (DataFrame): 填充后的CSV数据框
    """
    print("\n=== 统计信息 ===")
    
    # 显示JSON数据中的统计信息
    print(f"学科评估数据中有A类学科的学校总数: {len(school_a_counts)}")
    
    # 对学校按A类学科数量进行排序
    # sorted() 函数配合 key=lambda 可以按指定规则排序
    # x[1] 表示按元组的第二个元素（学科数量）排序，reverse=True 表示降序
    sorted_schools = sorted(school_a_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("\n学科评估A类学科数量排名（前10名）:")
    # enumerate() 可以同时获取索引和值，从1开始计数
    for i, (school, count) in enumerate(sorted_schools[:10], 1):
        # :2d 表示右对齐，占2位数字的格式
        print(f"  {i:2d}. {school}: {count} 个A类学科")
    
    # 从DataFrame中提取标准答案和AI答案列，转换为列表
    standard_answers = df['标准答案'].tolist()  # .tolist() 将pandas Series转换为Python列表
    ai_answers = df['AI答案'].tolist()
    
    # 显示CSV文件的统计信息
    print(f"\nCSV文件中学校总数: {len(df)}")
    # 列表推导式统计满足条件的元素数量
    print(f"有A类学科的学校数: {sum(1 for x in standard_answers if x > 0)}")
    print(f"无A类学科的学校数: {sum(1 for x in standard_answers if x == 0)}")
    
    # 计算AI回答的准确率
    # zip() 函数将两个列表配对，逐一比较标准答案和AI答案
    correct_count = sum(1 for std, ai in zip(standard_answers, ai_answers) if std == ai)
    accuracy = correct_count / len(df) * 100  # 计算准确率百分比
    print(f"\nAI回答准确率: {correct_count}/{len(df)} = {accuracy:.1f}%")
    
    # 找出不匹配的案例
    mismatches = []
    # enumerate() 同时获取索引和配对的答案
    for i, (std, ai) in enumerate(zip(standard_answers, ai_answers)):
        if std != ai:  # 如果标准答案与AI答案不一致
            school_name = df.iloc[i]['学校名称']  # df.iloc[i] 按位置索引获取第i行
            mismatches.append((school_name, std, ai))
    
    # 显示不匹配的案例
    if mismatches:
        print(f"\n不匹配的案例 ({len(mismatches)} 个):")
        # 只显示前10个不匹配的案例
        for school, std, ai in mismatches[:10]:
            print(f"  {school}: 标准答案={std}, AI答案={ai}")
        if len(mismatches) > 10:
            print(f"  ... 还有 {len(mismatches) - 10} 个不匹配")

def main():
    """
    主函数：程序的入口点，协调各个步骤的执行
    """
    # 配置文件路径
    # os.path.join() 用于构建跨平台兼容的文件路径
    # 获取当前脚本所在目录的上级目录（AI-hallucination）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(current_dir))  # 回到AI-hallucination目录
    json_file = os.path.join(base_dir, "src/data/subject_evaluation/subject_evaluation_data.json")
    csv_file = os.path.join(base_dir, "ai_evaluation_dataset_long_教育部评估A类学科数量_answers.csv")
    
    # 检查必要文件是否存在
    # os.path.exists() 检查文件或目录是否存在
    if not os.path.exists(json_file):
        print(f"错误: JSON文件不存在: {json_file}")
        return  # 提前退出函数
    
    if not os.path.exists(csv_file):
        print(f"错误: CSV文件不存在: {csv_file}")
        return
    
    try:
        # 步骤1：加载和处理学科评估数据
        print("正在加载学科评估数据...")
        school_a_counts = load_subject_evaluation_data(json_file)
        print(f"成功加载学科评估数据，共有 {len(school_a_counts)} 个学校拥有A类学科")
        
        # 步骤2：创建备份文件
        # datetime.now().strftime() 生成当前时间的字符串格式
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # 格式：20250628_162516
        backup_file = csv_file.replace('.csv', f'_backup_{timestamp}.csv')
        
        # shutil.copy2() 复制文件，保留元数据（如修改时间等）
        shutil.copy2(csv_file, backup_file)
        print(f"原文件已备份到: {backup_file}")
        
        # 步骤3：填充标准答案
        print("正在填充教育部评估A类学科数量标准答案...")
        result_df = fill_a_subject_counts(csv_file, school_a_counts)
        
        # 步骤4：显示详细统计信息
        display_statistics(school_a_counts, result_df)
        
        # 步骤5：显示处理结果预览
        print("\n填充结果预览:")
        # .head(10) 获取前10行数据
        # .to_string(index=False) 将DataFrame转换为字符串，不显示行索引
        print(result_df[['学校名称', '标准答案', 'AI答案']].head(10).to_string(index=False))
        
    except Exception as e:
        # 异常处理：捕获并显示错误信息
        print(f"处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()  # 打印详细的错误堆栈信息，便于调试

if __name__ == "__main__":
    main()

import os
import json
import pandas as pd


def calculate_accuracy(file_csv):
    df = pd.read_csv(file_csv)
    # 计算准确率的逻辑
    total_count = len(df)
    accurate_count = 0
    
    for index, row in df.iterrows():
        # 检查是否匹配（转换为字符串进行比较以避免类型问题）
        if str(row['标准答案']).strip() == str(row['AI答案']).strip():
            accurate_count += 1

    return accurate_count / total_count if total_count > 0 else 0

def main():
    # 获取当前脚本所在目录的上级目录（AI-hallucination）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(current_dir))  # 回到AI-hallucination目录
    
    file_name = 'ai_evaluation_dataset_long_学术型博士学位点_answers.csv'
    file_csv = os.path.join(base_dir, file_name)
    
    if not os.path.exists(file_csv):
        print(f"错误: 文件不存在 {file_csv}")
        return
    
    print(f"正在计算文件的准确率: {file_name}")
    
    accuracy = calculate_accuracy(file_csv)
    print("=" * 60)
    print(f"整体准确率: {accuracy:.2%}")

if __name__ == "__main__":
    main()
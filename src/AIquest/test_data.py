import sys
import os
import re
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.AIquest.utils.data_reader import DataReader

def debug_text_extraction():
    """调试文本提取过程"""
    data_reader = DataReader()
    
    # 使用绝对路径
    consolidated_file = os.path.join(project_root, "src", "data", "consolidated", "ESI前1%学科数量_data.json")
    
    print(f"🔍 测试文本提取功能")
    print(f"📂 项目根目录: {project_root}")
    print(f"📁 数据文件路径: {consolidated_file}")
    print(f"✅ 文件是否存在: {os.path.exists(consolidated_file)}")
    
    if os.path.exists(consolidated_file):
        # 调用文本提取方法
        extracted_text = data_reader.extract_text_content(consolidated_file)
        
        print(f"\n📝 提取结果:")
        print(f"文本长度: {len(extracted_text)} 字符")
        
        # 🔥 输出完整的提取文本（分段显示避免过长）🔥
        print(f"\n📄 完整提取文本:")
        print("=" * 80)
        
        # 按行显示，便于查看结构
        lines = extracted_text.split('\n')
        print(f"总行数: {len(lines)}")
        
        # 显示前50行
        print(f"\n📋 前50行:")
        print("-" * 60)
        for i, line in enumerate(lines[:50]):
            print(f"{i+1:3d}: {line}")
        
        # 🔥 查找并显示中山大学相关的完整数据块 🔥
        print(f"\n🎯 中山大学相关数据:")
        print("-" * 60)
        zhongshan_indices = []
        for i, line in enumerate(lines):
            if '中山大学' in line:
                zhongshan_indices.append(i)
        
        if zhongshan_indices:
            for idx in zhongshan_indices:
                print(f"找到中山大学在第{idx+1}行: {lines[idx]}")
                # 显示前后10行作为上下文
                start = max(0, idx-5)
                end = min(len(lines), idx+6)
                print(f"上下文 (第{start+1}-{end}行):")
                for j in range(start, end):
                    marker = ">>> " if j == idx else "    "
                    print(f"{marker}{j+1:3d}: {lines[j]}")
                print()
        
        # 🔥 搜索关键字段 🔥
        print(f"\n🔑 关键字段检查:")
        print("-" * 60)
        key_fields = ['前1%数', '前1‰数', '学校名', '全球排名', 'ESI']
        for field in key_fields:
            count = extracted_text.count(field)
            print(f"'{field}': 出现 {count} 次")
            if count > 0:
                # 显示前3个匹配的行
                matching_lines = [line for line in lines if field in line]
                print(f"  示例: {matching_lines[:3]}")
        
        # 🔥 检查数据质量 🔥
        print(f"\n📊 数据质量分析:")
        print("-" * 60)
        if '学校名' in extracted_text and '前1%数' in extracted_text:
            print(f"✅ 数据包含正确的字段结构")
        else:
            print(f"❌ 数据字段结构异常")
        
        if '中山大学' in extracted_text:
            print(f"✅ 提取的文本包含'中山大学'")
        else:
            print(f"❌ 提取的文本不包含'中山大学'")
        
        # 🔥 检查是否包含数字数据 🔥
        number_lines = [line for line in lines if any(char.isdigit() for char in line)]
        print(f"包含数字的行数: {len(number_lines)}")
        if len(number_lines) > 0:
            print(f"数字行示例:")
            for line in number_lines[:5]:
                print(f"  {line}")
        
        # 🔥 保存提取的文本到文件，便于详细查看 🔥
        output_file = os.path.join(project_root, "debug_extracted_text.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"ESI数据提取结果\n")
            f.write(f"=" * 80 + "\n")
            f.write(f"文件: {consolidated_file}\n")
            f.write(f"提取时间: {os.path.getctime(consolidated_file)}\n")
            f.write(f"文本长度: {len(extracted_text)} 字符\n")
            f.write(f"总行数: {len(lines)}\n")
            f.write(f"\n完整提取文本:\n")
            f.write("-" * 80 + "\n")
            f.write(extracted_text)
        
        print(f"\n💾 完整提取文本已保存到: {output_file}")
        
    else:
        print(f"❌ 文件不存在: {consolidated_file}")
        
        # 列出实际存在的文件
        consolidated_dir = os.path.join(project_root, "src", "data", "consolidated")
        if os.path.exists(consolidated_dir):
            print(f"📂 consolidated目录内容:")
            files = os.listdir(consolidated_dir)
            for file in files:
                file_path = os.path.join(consolidated_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"  - {file} ({file_size} bytes)")

if __name__ == "__main__":
    debug_text_extraction()
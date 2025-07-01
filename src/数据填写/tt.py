import json
import os

def fix_field_names(json_file_path):
    """
    修复JSON文件中的字段名编码问题
    将 "前%1数" 替换为 "前1%数"
    将 "前‰1数" 替换为 "前1‰数"
    """
    try:
        # 读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # 检查是否有results字段
        if 'results' not in data:
            print("未找到results字段")
            return False
        
        # 修复字段名
        fixed_count = 0
        for item in data['results']:
            # 检查并修复 "前%1数" -> "前1%数"
            if "前%1数" in item:
                item["前1%数"] = item.pop("前%1数")
                fixed_count += 1
            if "前％1数" in item:
                item["前1%数"] = item.pop("前％1数")
                fixed_count += 1
            if "前‰1数" in item:
                item["前1‰数"] = item.pop("前‰1数")
                fixed_count += 1 
            
        
        # 保存修复后的文件
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        
        print(f"修复完成！共修复了 {fixed_count} 个字段")
        return True
        
    except FileNotFoundError:
        print(f"文件未找到: {json_file_path}")
        return False
    except json.JSONDecodeError:
        print(f"JSON格式错误: {json_file_path}")
        return False
    except Exception as e:
        print(f"修复过程中出现错误: {str(e)}")
        return False

# 使用示例
if __name__ == "__main__":
    # 获取当前脚本所在目录的上级目录（AI-hallucination）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(current_dir))  # 回到AI-hallucination目录
    file_path = os.path.join(base_dir, "src/data/consolidated/ESI前1%学科数量_data.json")
    fix_field_names(file_path)

"""文件操作工具"""
import os
import json
import csv
from src.AIquest.config import OUTPUT_CONFIG


class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def save_json_data(data, output_path):
        """保存数据到JSON文件，包含验证和原子写入"""
        def validate_json_data(data_to_validate):
            try:
                json.dumps(data_to_validate, ensure_ascii=False)
                return True
            except TypeError as e:
                print(f"错误: 数据中包含无法JSON序列化的类型 - {e}")
                return False
            except Exception as e:
                print(f"JSON验证时发生未知错误: {e}")
                return False

        if not validate_json_data(data):
            print(f"错误: 提供的数据未能通过JSON验证。文件 {output_path} 未保存。")
            return False

        temp_output_path = output_path + '.tmp'
        try:
            with open(temp_output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=OUTPUT_CONFIG['json_indent'], sort_keys=True)
            
            # 验证写入的临时文件
            with open(temp_output_path, 'r', encoding='utf-8') as f_check:
                json.load(f_check)
            
            os.replace(temp_output_path, output_path)
            print(f"成功: 数据已保存到 {output_path}")
            return True
            
        except json.JSONDecodeError as e:
            print(f"错误: 写入的内容不是有效的JSON: {e}")
            if os.path.exists(temp_output_path):
                os.remove(temp_output_path)
            return False
        except Exception as e:
            print(f"保存JSON文件 {output_path} 时发生错误: {e}")
            if os.path.exists(temp_output_path):
                try:
                    os.remove(temp_output_path)
                except OSError:
                    pass
            return False
    
    @staticmethod
    def count_text_characters(json_file_path):
        """统计JSON文件中的文本字符数"""
        if not os.path.exists(json_file_path):
            print(f"错误：JSON文件未找到 {json_file_path}")
            return 0

        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"错误：无法解析JSON文件 {json_file_path}: {e}")
            return 0
        except Exception as e:
            print(f"读取JSON文件时发生错误 {json_file_path}: {e}")
            return 0

        def count_characters_in_value(value):
            count = 0
            if isinstance(value, str):
                count += len(value)
            elif isinstance(value, list):
                for item in value:
                    count += count_characters_in_value(item)
            elif isinstance(value, dict):
                for v in value.values():
                    count += count_characters_in_value(v)
            return count

        return count_characters_in_value(data)
    
    @staticmethod
    def merge_csv_files(csv_files, output_path):
        """合并多个CSV文件"""
        all_data = []
        fieldnames = None
        
        for csv_file in csv_files:
            try:
                with open(csv_file, mode='r', encoding=OUTPUT_CONFIG['file_encoding']) as csvfile:
                    reader = csv.DictReader(csvfile)
                    if fieldnames is None:
                        fieldnames = reader.fieldnames
                    
                    for row in reader:
                        all_data.append(row)
            except Exception as e:
                print(f"读取CSV文件 {csv_file} 失败: {e}")
        
        if all_data and fieldnames:
            try:
                with open(output_path, mode='w', encoding=OUTPUT_CONFIG['file_encoding'], newline='') as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(all_data)
                print(f"成功合并 {len(all_data)} 条记录到: {output_path}")
                return True
            except Exception as e:
                print(f"写入合并结果失败: {e}")
                return False
        
        return False
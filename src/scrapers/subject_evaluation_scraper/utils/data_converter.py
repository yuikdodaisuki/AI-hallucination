"""数据格式转换工具"""
import json
import traceback


class DataConverter:
    """数据格式转换器"""
    
    @staticmethod
    def convert_to_flat_format(input_data):
        """将层级数据转换为扁平格式"""
        formatted_data = []
        
        # 遍历所有学科类别
        for category, subjects in input_data.items():
            # 遍历该类别下的所有学科
            for subject, ratings in subjects.items():
                # 提取学科代码和名称
                subject_parts = subject.split(maxsplit=1)
                subject_code = subject_parts[0] if subject_parts else ""
                subject_name = subject_parts[1] if len(subject_parts) > 1 else ""
                
                # 遍历该学科下的所有评级
                for rating, schools in ratings.items():
                    # 遍历该评级下的所有学校
                    for school in schools:
                        record = {
                            "subject_name": subject_name,
                            "rating": rating,
                            "school_name": school.get("name", "")
                        }
                        formatted_data.append(record)
        
        return formatted_data
    
    @staticmethod
    def save_json(data, filepath):
        """保存数据为JSON文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"成功保存数据到 {filepath}")
            return True
        except Exception as e:
            print(f"保存数据时发生错误: {e}")
            traceback.print_exc()
            return False
    
    @staticmethod
    def load_json(filepath):
        """加载JSON文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载数据时发生错误: {e}")
            traceback.print_exc()
            return None
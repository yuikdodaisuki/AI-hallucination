"""数据提取器"""
import os
import traceback
from .utils.driver_manager import DriverManager
from .utils.page_parser import PageParser
from .utils.data_converter import DataConverter
from .config import TARGET_URL, OUTPUT_DIR, RAW_FILENAME, PROCESSED_FILENAME, DEBUG_FILES, OUTPUT_OPTIONS


class SubjectEvaluationExtractor:
    """学科评估数据提取器"""
    
    def __init__(self):
        self.ensure_output_directory()
    
    def ensure_output_directory(self):
        """确保输出目录存在"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(current_dir, OUTPUT_DIR)
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"确保输出目录存在: {self.output_dir}")
    
    def extract_raw_data(self, save_to_file=None):
        """提取原始数据
        
        Args:
            save_to_file: 是否保存到文件，None时使用配置决定
        """
        should_save = save_to_file if save_to_file is not None else OUTPUT_OPTIONS['save_raw_data']
        try:
            with DriverManager() as driver_manager:
                # 导航到主页面
                driver_manager.navigate_to_page(TARGET_URL)
                
                # 导航到iframe
                iframe_url = driver_manager.navigate_to_iframe(
                    TARGET_URL, 
                    '.yxphb', 
                    'iframe'
                )
                
                # 保存iframe内容用于调试
                driver_manager.save_page_source(
                    os.path.join(self.output_dir, DEBUG_FILES['iframe_content'])
                )
                
                # 创建页面解析器
                parser = PageParser(driver_manager.driver)
                
                # 提取数据
                result_data = self._extract_all_categories(parser)
                
                # 根据配置决定是否保存
                if should_save:
                    raw_filepath = os.path.join(self.output_dir, RAW_FILENAME)
                    if DataConverter.save_json(result_data, raw_filepath):
                        print(f"✅ 原始数据已保存: {raw_filepath}")
                    else:
                        print("❌ 原始数据保存失败")
                        return None
                else:
                    print("ℹ️ 根据配置，跳过原始数据保存")
                
                return result_data
                    
        except Exception as e:
            print(f"提取数据过程中发生错误: {e}")
            traceback.print_exc()
            
            # 保存错误页面
            try:
                with DriverManager() as error_driver:
                    error_driver.save_page_source(
                        os.path.join(self.output_dir, DEBUG_FILES['error_page'])
                    )
            except:
                pass
            
            return None
    
    def _extract_all_categories(self, parser):
        """提取所有学科类别的数据"""
        result_data = {}
        
        # 获取所有学科类别
        category_elements = parser.get_category_elements()
        
        for i in range(len(category_elements)):
            # 重新获取当前学科类别元素
            current_category_element = parser.get_category_elements()[i]
            category_name = current_category_element.text.strip()
            print(f"处理学科类别: {category_name}")
            
            # 点击学科类别
            parser.click_and_wait(current_category_element)
            
            # 提取该类别下的所有学科数据
            category_data = self._extract_category_subjects(parser)
            result_data[category_name] = category_data
        
        return result_data
    
    def _extract_category_subjects(self, parser):
        """提取类别下的所有学科数据"""
        category_data = {}
        
        # 获取该类别下的所有学科
        subject_elements = parser.get_subject_elements()
        
        for j in range(len(subject_elements)):
            # 重新获取当前学科元素
            current_subject_element = parser.get_subject_elements()[j]
            subject_code_name = current_subject_element.text.strip()
            print(f"  处理学科: {subject_code_name}")
            
            # 点击学科
            parser.click_and_wait(current_subject_element)
            
            # 解析评估结果
            evaluation_results = parser.parse_evaluation_results()
            category_data[subject_code_name] = evaluation_results
        
        return category_data
    
    def convert_data_format(self, input_data=None, save_to_file=None):
        """转换数据格式
        
        Args:
            input_data: 输入数据，None时从文件读取
            save_to_file: 是否保存到文件，None时使用配置决定
        """
        should_save = save_to_file if save_to_file is not None else OUTPUT_OPTIONS['save_processed_data']
        try:
            # 获取数据源
            if input_data is not None:
                raw_data = input_data
                print("使用传入的原始数据进行转换")
            else:
                # 从文件加载
                raw_filepath = os.path.join(self.output_dir, RAW_FILENAME)
                raw_data = DataConverter.load_json(raw_filepath)
                if raw_data is None:
                    print("❌ 无法加载原始数据文件")
                    return None
                print("从文件加载原始数据进行转换")
            
            # 转换为扁平格式
            formatted_data = DataConverter.convert_to_flat_format(raw_data)
            
            # 根据配置决定是否保存
            if should_save:
                processed_filepath = os.path.join(self.output_dir, PROCESSED_FILENAME)
                if DataConverter.save_json(formatted_data, processed_filepath):
                    print(f"✅ 转换后数据已保存: {processed_filepath}")
                    return formatted_data
                else:
                    print("❌ 转换后数据保存失败")
                    return None
            else:
                print("ℹ️ 根据配置，跳过转换后数据保存")
                return formatted_data
            
        except Exception as e:
            print(f"转换数据格式时发生错误: {e}")
            traceback.print_exc()
            return None
    
    def extract_and_convert(self, output_format=None):
        """完整的提取和转换流程
        
        Args:
            output_format: 输出格式 'raw', 'processed', 'both'，None时使用配置
        """
        format_option = output_format or OUTPUT_OPTIONS['output_format']
        auto_convert = OUTPUT_OPTIONS['auto_convert']
        
        print(f"🚀 开始提取学科评估数据 (格式: {format_option})...")
        
        results = {}
        
        # 第一步：提取原始数据
        if format_option in ['raw', 'both']:
            print("\n📥 提取原始数据...")
            raw_data = self.extract_raw_data(save_to_file=True)
            if raw_data is None:
                print("❌ 原始数据提取失败")
                return None
            results['raw_data'] = raw_data
        else:
            # 即使不输出原始数据，也需要提取用于转换
            print("\n📥 提取数据用于转换...")
            raw_data = self.extract_raw_data(save_to_file=False)
            if raw_data is None:
                print("❌ 数据提取失败")
                return None
        
        # 第二步：转换数据格式
        if format_option in ['processed', 'both'] and auto_convert:
            print("\n🔄 转换数据格式...")
            # 使用刚提取的原始数据进行转换，避免重复读取文件
            processed_data = self.convert_data_format(
                input_data=raw_data, 
                save_to_file=True
            )
            if processed_data is None:
                print("❌ 数据格式转换失败")
                return None
            results['processed_data'] = processed_data
        
        print(f"\n✅ 学科评估数据提取完成! (格式: {format_option})")
        return results if len(results) > 1 else (results.get('raw_data') or results.get('processed_data'))
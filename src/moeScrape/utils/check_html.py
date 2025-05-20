import json
import re


def find_initPubProperty(soup):
    params_list = []
    script_content = ""
    # 找到包含目标函数的脚本
    for script in soup.find_all('script'):
        if script.string and 'initPubProperty' in script.string:
            script_content = script.string
            break

    if script_content:
        # 提取函数调用部分
        function_call_pattern = r'initPubProperty\s*\(([\s\S]*?)\);'
        matches = re.search(function_call_pattern, script_content)

        if matches:
            params_str = matches.group(1)

            # 处理JavaScript对象参数
            # 这部分需要根据实际参数格式调整
            try:
                # 对于简单的JSON对象参数
                if params_str.strip().startswith('{') and params_str.strip().endswith('}'):
                    # 将JS对象转换为Python字典
                    params_str = params_str.replace("'", '"')  # JS中的单引号转换为双引号
                    params = json.loads(params_str)
                    print("解析的参数对象:", params)

                # 对于多个参数的情况
                else:
                    # 尝试将参数拆分并解析
                    # 注意：这种方法对于复杂参数可能不可靠
                    # params_list = []   在函数开始定义，以便后续使用
                    # 简单的逗号分隔可能不适用于包含对象或数组的参数
                    for param in params_str.split(','):
                        param = param.strip()
                        if param.startswith('{') and param.endswith('}'):
                            # 尝试解析JSON对象
                            param = param.replace("'", '"')
                            params_list.append(json.loads(param))
                        elif param.startswith('[') and param.endswith(']'):
                            # 尝试解析数组
                            param = param.replace("'", '"')
                            params_list.append(json.loads(param))
                        elif param.lower() == 'true':
                            params_list.append(True)
                        elif param.lower() == 'false':
                            params_list.append(False)
                        elif param.isdigit():
                            params_list.append(int(param))
                        elif param == 'null':
                            params_list.append(None)
                        else:
                            # 尝试解析为字符串
                            if param.startswith('"') and param.endswith('"'):
                                params_list.append(param[1:-1])
                            elif param.startswith("'") and param.endswith("'"):
                                params_list.append(param[1:-1])
                            else:
                                params_list.append(param)

                    # print("解析的参数列表:", params_list)
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                print(f"原始参数字符串: {params_str}")
        else:
            print("未找到函数调用")
    else:
        print("未找到包含initPubProperty的脚本")

    return params_list


# 判断页面是否是 src site
def is_src_site_format(soup):
    return bool(soup.find('div', id='downloadContent'))


# 判断页面是否是jyb
def is_jyb_format(soup):
    return bool(soup.find('div', class_='moe-detail-box'))
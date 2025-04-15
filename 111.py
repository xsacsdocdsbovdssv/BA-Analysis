import json
import pandas as pd
import re

# 读取 JSON 文件
with open('semantic_relations1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 处理语义关系数据
def process_semantic_data(relation_list):
    processed_rows = []

    for item in relation_list:
        if len(item) == 3:  # 确保是三元组
            word1, word2, description = item

            # 初始化结果字典
            result = {
                '第一词': word1,
                '第二词': word2,
                '关系类型': None,
                '得分': None,
                '阈值': None,
                '是否超过阈值': None
            }

            # 检测反义关系
            antonym_match = re.search(r'反义对立度:\s*([\d.]+).*?阈值>\s*([\d.]+)', description)
            if antonym_match:
                result.update({
                    '关系类型': '反义',
                    '得分': float(antonym_match.group(1)),
                    '阈值': float(antonym_match.group(2)),
                    '是否超过阈值': float(antonym_match.group(1)) > float(antonym_match.group(2))
                })

            # 检测同义关系
            synonym_match = re.search(r'同义置信度:\s*([\d.]+).*?阈值>\s*([\d.]+)', description)
            if synonym_match:
                result.update({
                    '关系类型': '同义',
                    '得分': float(synonym_match.group(1)),
                    '阈值': float(synonym_match.group(2)),
                    '是否超过阈值': float(synonym_match.group(1)) > float(synonym_match.group(2))
                })

            processed_rows.append(result)

    return pd.DataFrame(processed_rows)

# 处理数据
if isinstance(data, dict):
    # 如果数据是字典，尝试获取antonym_groups或其他可能的键
    relation_data = data.get('antonym_groups', []) + data.get('synonym_groups', [])
    df = process_semantic_data(relation_data)
elif isinstance(data, list):
    # 如果数据直接是列表
    df = process_semantic_data(data)
else:
    print("数据格式不符合预期，请检查JSON结构")
    exit()

# 保存到Excel
output_file = 'semantic_relations.xlsx'
df.to_excel(output_file, index=False)
print(f"处理完成，共{len(df)}条记录，结果已保存到 {output_file}")
print("包含的关系类型统计:")
print(df['关系类型'].value_counts())
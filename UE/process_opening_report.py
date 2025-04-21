import pandas as pd

# 当在营业系统下载好的门店报表经过原始店名匹配后
# 需要删除第2、3行，保留原始店名，保留省份，保留营业天数，保留订单数，保留经营指标
# 返回处理后的文件路径
def process_opening_report(file_path: str, output_path: str = None) -> str:
    # 读取Excel文件
    df = pd.read_excel(file_path, header=0)

    # 删除第2、3行（Excel的第2、3行是索引1、2）
    df.drop(index=[0, 1], inplace=True, errors='ignore')
    df.reset_index(drop=True, inplace=True)

    # 保留的列名
    keep_columns = [
        "店名", "原始店名", "营业天数",
        "订单数.1", "订单数.2", "订单数.3",
        "经营指标", "省份"
    ]

    # 只保留需要的列，存在的列中进行筛选
    df = df[[col for col in keep_columns if col in df.columns]]

    # 保存结果
    if not output_path:
        output_path = file_path.replace(".xlsx", "_processed.xlsx")
    df.to_excel(output_path, index=False)
    return output_path

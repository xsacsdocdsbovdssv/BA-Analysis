import pandas as pd

def merge_opening_data_into_financial_report(financial_file: str, opening_file: str, output_file: str = None) -> str:
    # 加载两个文件
    df_fin = pd.read_excel(financial_file)
    df_open = pd.read_excel(opening_file)

    # 确保“原始店名”为字符串
    df_fin["原始店名"] = df_fin["原始店名"].astype(str)
    df_open["原始店名"] = df_open["原始店名"].astype(str)

    # 选取开台表需要的字段，并重命名，防止冲突
    df_open_extract = df_open[[
        "原始店名", "营业天数", "订单数.1", "订单数.2", "订单数.3", "经营指标"
    ]].copy()

    df_open_extract.rename(columns={
        "营业天数": "开台_营业天数",
        "订单数.1": "开台_订单数1",
        "订单数.2": "开台_订单数2",
        "订单数.3": "开台_订单数3",
        "经营指标": "开台_经营指标"
    }, inplace=True)

    # 合并
    df_merged = pd.merge(df_fin, df_open_extract, on="原始店名", how="left")

    # 写入合并结果到财务报表字段
    df_merged["营业天数"] = df_merged["开台_营业天数"]
    df_merged["日均开台数"] = df_merged["开台_订单数1"] + df_merged["开台_经营指标"]
    df_merged["日均外卖单数"] = df_merged["开台_订单数2"] + df_merged["开台_订单数3"]

    # 删除“开台_”前缀列
    df_merged.drop(columns=[
        "开台_营业天数", "开台_订单数1", "开台_订单数2", "开台_订单数3", "开台_经营指标"
    ], inplace=True)

    # 保存结果
    if not output_file:
        output_file = financial_file.replace(".xlsx", "_merged.xlsx")
    df_merged.to_excel(output_file, index=False)

    return output_file

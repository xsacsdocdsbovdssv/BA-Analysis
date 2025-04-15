import pandas as pd

class ExcelProcessor:
    def __init__(self, main_file_path, lookup_file_path, sheet_name='Sheet1'):
        self.main_file_path = main_file_path
        self.lookup_file_path = lookup_file_path
        self.sheet_name = sheet_name

    def process(self, output_path=None):
        # 读取主文件
        df = pd.read_excel(self.main_file_path)

        # 读取查找文件（G:I列）
        lookup_df = pd.read_excel(self.lookup_file_path, sheet_name=self.sheet_name, usecols="G:I")

        # 为第一列加列名“店名”
        if df.columns[0] != "店名":
            df.columns.values[0] = "店名"

        # 构建字典，key = G列（第1列），value = I列（第3列）
        lookup_dict = pd.Series(lookup_df.iloc[:, 2].values, index=lookup_df.iloc[:, 0]).to_dict()

        # 新增一列“原始店名”
        df.insert(1, "原始店名", df["店名"].map(lambda x: lookup_dict.get(x, x)))

        # 输出文件路径
        if not output_path:
            output_path = self.main_file_path  # 默认覆盖原文件

        # 保存结果
        df.to_excel(output_path, index=False)

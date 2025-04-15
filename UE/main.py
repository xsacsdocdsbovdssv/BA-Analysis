from process_financial_report import process_financial_report
from process_storename import ExcelProcessor_zhuanhegui
# 使用示例
if __name__ == "__main__":
    input1_file = "/Users/zhaozhilong/Desktop/work/半天妖/其他/商业分析/基础文档/管理报表/半天妖2025.03上交管理表完整版 - 不含#号.xlsx"
    input2_file = "/Users/zhaozhilong/Desktop/work/半天妖/其他/商业分析/基础文档/开台数/门店报表364f0ff24d0a4342a8a5d4b50cb8cc66.xlsx"
    lookup_file = "/Users/zhaozhilong/Desktop/work/半天妖/其他/商业分析/基础文档/转合规/转合规529+2家-2家店名3月.xlsx"

    try:
        # result_file = process_financial_report(input1_file)
        # print("处理完成process_financial_report")
        # processor = ExcelProcessor_zhuanhegui(result_file, lookup_file)
        # processor.process(result_file)
        result_file = input2_file
        processor = ExcelProcessor_zhuanhegui(result_file, lookup_file)
        processor.process(result_file)

        print("处理完成process_storename")
        print(f"处理完成，结果文件: {input2_file}")
    except Exception as e:
        print(f"处理失败: {str(e)}")
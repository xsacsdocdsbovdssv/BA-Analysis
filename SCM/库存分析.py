import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib import rcParams

# 设置中文字体
try:
    rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'SimHei', 'Arial Unicode MS']
    rcParams['axes.unicode_minus'] = False
except:
    print("中文字体设置失败，图表可能无法正常显示中文")

def load_and_preprocess(filepath):
    try:
        df_raw = pd.read_excel(filepath, header=0)
        df = df_raw.set_index('Unnamed: 0').T
        df.columns = ['期末结存金额', '鱼结存金额', '鱼结存占比', '实收金额']

        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df.index.name = '月份'
        df.reset_index(inplace=True)

        def convert_month_format(x):
            x = str(x).strip()
            if '.' in x:
                parts = x.split('.')
                if len(parts) == 2:
                    year, month = parts
                    year = year if len(year) == 4 else f"20{year.zfill(2)}"
                    month = month.zfill(2)
                    return f"{year}-{month}"
            elif '-' in x:
                return x
            return x

        df['月份'] = df['月份'].apply(convert_month_format)
        df['月份'] = pd.to_datetime(df['月份'], format="%Y-%m", errors='coerce')

        return df.dropna()
    except Exception as e:
        print(f"数据加载错误: {str(e)}")
        return None

def plot_inventory_analysis(df):
    # 设置图形样式
    try:
        plt.style.use('ggplot')
    except:
        plt.style.use('default')

    fig, axs = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('库存分析报告', fontsize=16)

    # 设置日期格式
    months = mdates.MonthLocator(interval=2)
    month_fmt = mdates.DateFormatter('%y-%m')

    # 图1：库存金额趋势
    ax1 = axs[0,0]
    ax1.plot(df['月份'], df['期末结存金额']/1e8, label='总库存', marker='o')# 设置总库存为蓝色点
    ax1.plot(df['月份'], df['鱼结存金额']/1e8, label='鱼类库存', marker='s')# 设置鱼类库存为绿色方块
    ax1.plot(df['月份'], df['实收金额']/1e8, label='总实收', marker='^')# 设置总实收为红色三角
    ax1.set_title('库存金额趋势（亿元）')
    ax1.set_ylabel('金额（亿元）')
    ax1.legend()
    ax1.grid(True)
    ax1.xaxis.set_major_locator(months)
    ax1.xaxis.set_major_formatter(month_fmt)

    # 图2：鱼类库存占比
    ax2 = axs[0,1]
    ax2.plot(df['月份'], df['鱼结存占比']*100, color='green', marker='^')
    ax2.set_title('鱼类库存占比趋势')
    ax2.set_ylabel('占比（%）')
    ax2.grid(True)
    ax2.xaxis.set_major_locator(months)
    ax2.xaxis.set_major_formatter(month_fmt)

    # 图3：环比增长率
    ax3 = axs[1, 0]
    ax3.plot(df['月份'], df['期末结存环比']*100, label='总库存环比')
    ax3.plot(df['月份'], df['鱼结存环比']*100, label='鱼类库存环比')
    ax3.axhline(0, color='gray', linestyle='--')
    ax3.set_title('库存环比增长率')
    ax3.set_ylabel('增长率（%）')
    ax3.legend()
    ax3.grid(True)
    ax3.xaxis.set_major_locator(months)
    ax3.xaxis.set_major_formatter(month_fmt)

    # 图4：鱼类占比平滑分析
    ax4 = axs[1, 1]
    ax4.plot(df['月份'], df['鱼结存占比']*100, alpha=0.3, label='原始占比')
    ax4.plot(df['月份'], df['鱼占比滑动平均']*100, color='red', label='3期移动平均')
    ax4.set_title('鱼类占比平滑分析')
    ax4.set_ylabel('占比（%）')
    ax4.legend()
    ax4.grid(True)
    ax4.xaxis.set_major_locator(months)
    ax4.xaxis.set_major_formatter(month_fmt)

    # 所有子图：统一格式化X轴
    for ax in axs.flat:
        ax.xaxis.set_major_locator(months)
        ax.xaxis.set_major_formatter(month_fmt)
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_horizontalalignment('right')

    plt.tight_layout()

    # 尝试不同的显示方式
    try:
        plt.show()
    except:
        try:
            plt.savefig('inventory_analysis2.png')
            print("图表已保存为 inventory_analysis2.png")
        except Exception as e:
            print(f"无法显示或保存图表: {str(e)}")



if __name__ == "__main__":
    filepath = "/Users/zhaozhilong/Desktop/work/半天妖/其他/商业分析/中心与供应商对账/中心与供应商对账表/工作簿122.xlsx"

    df = load_and_preprocess(filepath)

    if df is not None:
        print("数据加载成功，前5行示例：")
        print(df.head())

        df['期末结存环比'] = df['期末结存金额'].pct_change()
        df['鱼结存环比'] = df['鱼结存金额'].pct_change()
        df['鱼占比滑动平均'] = df['鱼结存占比'].rolling(window=3, min_periods=1).mean()

        plot_inventory_analysis(df)
    else:
        print("数据加载失败，无法进行库存分析。")
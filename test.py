
import plotly.graph_objects as go
import pandas as pd

# 示例数据
data = {
    '时间': ['2024-01-01', '2024-01-02', '2024-01-03'],
    '开盘价': [100, 101, 102],
    '收盘价': [102, 103, 101],
    '最高价': [103, 104, 105],
    '最低价': [99, 100, 99]
}
df = pd.DataFrame(data)

# 创建一个空的图
fig = go.Figure()

# 遍历 DataFrame 中的每一行
for index, row in df.iterrows():
    # 绘制 K 线图的四个部分
    fig.add_shape(
        type='line',  # 线段
        x0=row['时间'], y0=row['开盘价'],
        x1=row['时间'], y1=row['收盘价'],
        xref='x', yref='y',
        line=dict(color='blue', width=4)
    )
    fig.add_shape(
        type='line',  # 上影线
        x0=row['时间'], y0=row['最高价'],
        x1=row['时间'], y1=row['开盘价'] if row['开盘价'] < row['收盘价'] else row['收盘价'],
        xref='x', yref='y',
        line=dict(color='gray', width=1)
    )
    fig.add_shape(
        type='line',  # 下影线
        x0=row['时间'], y0=row['最低价'],
        x1=row['时间'], y1=row['开盘价'] if row['开盘价'] > row['收盘价'] else row['收盘价'],
        xref='x', yref='y',
        line=dict(color='gray', width=1)
    )

# 设置图表的标题和坐标轴标签
fig.update_layout(
    title='K 线图示例',
    xaxis_title='时间',
    yaxis_title='价格'
)

# 显示图表
fig.show()
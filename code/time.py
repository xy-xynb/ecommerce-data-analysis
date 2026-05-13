import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ===================== 1. 数据读取与预处理 =====================
# 这里先给你一个测试用的模拟数据，确认能跑通
# 你后面可以把下面这段替换成读取你自己的 data_cleaned.csv
np.random.seed(42)
# 模拟电商用户行为数据：时间戳 + 行为类型
time_range = pd.date_range(start='2025-01-01', periods=50000, freq='min')
behavior_types = ['浏览', '收藏', '加购', '购买']
df = pd.DataFrame({
    'time': np.random.choice(time_range, size=50000),
    'behavior': np.random.choice(behavior_types, size=50000, p=[0.7, 0.1, 0.15, 0.05])
})

# -------------- 替换为你的真实数据 --------------
# df = pd.read_csv('data_cleaned.csv')
# 注意：如果你的列名不是 'time' 和 'behavior'，请手动修改下面这两个变量
time_col = 'time'       # 你的时间列名
behavior_col = 'behavior' # 你的行为类型列名

# 强制转换时间格式，避免解析失败
df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
# 去掉解析失败的无效时间
df = df.dropna(subset=[time_col])
# 提取小时（0-23）
df['hour'] = df[time_col].dt.hour

# ===================== 2. 统计24小时各行为类型分布 =====================
# 按小时+行为类型统计数量，确保0-23小时都存在
hour_behavior = df.groupby(['hour', behavior_col]).size().unstack(fill_value=0)
# 补全所有小时（防止某些小时没有数据导致缺失）
hour_behavior = hour_behavior.reindex(range(24), fill_value=0)
# 按小时统计总行为量
hour_total = hour_behavior.sum(axis=1)

# 打印关键统计信息
print("===== 24小时总行为量 =====")
print(hour_total)
print("\n===== 高峰时段 TOP5 =====")
peak_hours = hour_total.sort_values(ascending=False).head(5)
for i, (hour, cnt) in enumerate(peak_hours.items(), 1):
    print(f"第{i}名：{hour:2d}点，行为量 {cnt} 次")

# ===================== 3. 修复版可视化（避免pandas plot兼容性问题） =====================
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']  # 支持中文
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(14, 7))

# 1. 绘制堆叠柱状图（各行为类型分布）
bottom = np.zeros(24)
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
for i, col in enumerate(hour_behavior.columns):
    ax.bar(range(24), hour_behavior[col], bottom=bottom, label=col,
           color=colors[i % len(colors)], alpha=0.8)
    bottom += hour_behavior[col]

# 2. 绘制总行为量折线（标记高峰）
ax2 = ax.twinx()
ax2.plot(range(24), hour_total, color='red', linewidth=3, marker='o', markersize=8, label='总行为量')

# 设置图表样式
ax.set_title('24小时电商用户行为分布与高峰时段分析', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('小时（0-23）', fontsize=12)
ax.set_ylabel('各行为类型数量', fontsize=12)
ax2.set_ylabel('总行为量（次）', fontsize=12, color='red')
ax2.tick_params(axis='y', labelcolor='red')

# X轴设置
ax.set_xticks(range(24))
ax.set_xticklabels([f'{h}' for h in range(24)], rotation=0)
ax.grid(alpha=0.3, axis='y')

# 合并图例
handles1, labels1 = ax.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax.legend(handles1 + handles2, labels1 + labels2, loc='upper left', fontsize=10)

# 标注最高峰
max_hour = hour_total.idxmax()
max_count = hour_total.max()
ax2.annotate(f'最高峰\n{max_hour}点\n{max_count}次',
             xy=(max_hour, max_count),
             xytext=(max_hour+1, max_count+max_count*0.05),
             arrowprops=dict(arrowstyle='->', color='red', lw=2),
             fontsize=12, color='red', fontweight='bold')

plt.tight_layout()
plt.savefig('24小时行为分布与高峰时段.png', dpi=300, bbox_inches='tight')
plt.show()

# ===================== 4. 导出统计结果到Excel =====================
with pd.ExcelWriter('24小时用户行为分析结果.xlsx', engine='openpyxl') as writer:
    hour_behavior.to_excel(writer, sheet_name='各小时行为类型分布')
    hour_total.to_frame('总行为量').to_excel(writer, sheet_name='各小时总行为量')
    peak_hours.to_frame('行为量').to_excel(writer, sheet_name='高峰时段TOP5')

print("\n 分析完成！")
print(" 已生成：24小时行为分布与高峰时段.png")
print(" 已导出：24小时用户行为分析结果.xlsx")
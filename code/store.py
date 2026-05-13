import pandas as pd
import matplotlib.pyplot as plt

# ---------------------- 1. 读取数据 ----------------------
df = pd.read_csv('data_cleaned.csv')

# 电商用户行为数据最常见的列名，直接适配
behavior_col = 'behavior_type'  # 行为类型列，比如：pv、cart、fav、buy
category_col = 'category_id'    # 商品类别列

# 打印列名，确认是否匹配
print(f"✅ 行为列：{behavior_col}")
print(f"✅ 类别列：{category_col}")

# ---------------------- 2. 筛选浏览、购买行为 ----------------------
# 适配电商数据常见的行为编码：pv=浏览，buy=购买
browse = df[df[behavior_col] == 'pv']
buy = df[df[behavior_col] == 'buy']

# ---------------------- 3. 按类别统计 ----------------------
# 各分类浏览量
browse_cnt = browse.groupby(category_col).size().reset_index(name='浏览量')

# 各分类购买量
buy_cnt = buy.groupby(category_col).size().reset_index(name='购买量')

# 合并数据（没有购买的分类填充0）
result = pd.merge(browse_cnt, buy_cnt, on=category_col, how='left').fillna(0)

# 计算购买转化率（购买量 / 浏览量，保留2位小数）
result['购买转化率'] = (result['购买量'] / result['浏览量']).round(4)
result['购买转化率'] = result['购买转化率'].apply(lambda x: f"{x:.2%}")

# 按购买量降序排序
result = result.sort_values('购买量', ascending=False).reset_index(drop=True)

# ---------------------- 4. 输出结果 ----------------------
print("\n" + "="*80)
print("📊 各分类 浏览量 / 购买量 / 购买转化率（按购买量降序）")
print("="*80)
print(result.to_string(index=False))

# ---------------------- 5. 导出Excel ----------------------
result.to_excel('各分类购买转化率统计.xlsx', index=False, engine='openpyxl')

# ---------------------- 6. 可视化Top10分类 ----------------------
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

top10 = result.head(10)

fig, ax1 = plt.subplots(figsize=(14, 6))

# 柱状图：购买量
ax1.bar(top10[category_col].astype(str), top10['购买量'], color='#ff7f0e', alpha=0.7, label='购买量')
ax1.set_ylabel('购买量', fontsize=12)
ax1.tick_params(axis='x', rotation=45)

# 折线图：转化率
ax2 = ax1.twinx()
conv_rates = pd.to_numeric(top10['购买转化率'].str.replace('%', ''))
ax2.plot(top10[category_col].astype(str), conv_rates, color='red', marker='o', linewidth=3, label='转化率(%)')
ax2.set_ylabel('购买转化率(%)', fontsize=12, color='red')
ax2.tick_params(axis='y', labelcolor='red')

plt.title('Top10 分类 购买量 & 转化率', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('分类购买量与转化率.png', dpi=300)
plt.show()

print("\n 统计完成！")
print(" 已导出：各分类购买转化率统计.xlsx")
print(" 已生成：分类购买量与转化率.png")
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ---------------------- 1. 读取数据（适配你的列名） ----------------------
df = pd.read_csv('data_cleaned.csv')

# 确认你的关键列名
user_col = 'user_id'       # 用户ID
date_col = 'date'          # 日期列（你的数据里是date）
# 这里假设所有数据都是购买行为（如果有行为类型列，你可以告诉我名字，我帮你加上筛选）
buy_df = df.copy()

# 转换日期格式
buy_df[date_col] = pd.to_datetime(buy_df[date_col])

# ---------------------- 2. 计算 R（最近购买时间）和 F（购买频次） ----------------------
# 数据中最晚的日期作为"今天"
today = buy_df[date_col].max()

# 按用户聚合，计算最近购买时间和购买次数
user_rf = buy_df.groupby(user_col).agg(
    最近购买时间=(date_col, 'max'),
    购买频次=(date_col, 'count')
).reset_index()

# 计算距离今天的天数
user_rf['距今天数'] = (today - user_rf['最近购买时间']).dt.days

# ---------------------- 3. 定义分层规则 ----------------------
# R规则：30天内购买=高，超过30天=低
user_rf['R等级'] = user_rf['距今天数'].apply(lambda x: '高' if x <= 30 else '低')

# F规则：购买≥2次=高，仅1次=低
user_rf['F等级'] = user_rf['购买频次'].apply(lambda x: '高' if x >= 2 else '低')

# 分层逻辑
def get_user_segment(r_level, f_level):
    if r_level == '高' and f_level == '高':
        return '高价值用户'
    elif r_level == '高' and f_level == '低':
        return '潜力用户'
    elif r_level == '低' and f_level == '高':
        return '沉睡用户'
    else:
        return '流失用户'

user_rf['用户分层'] = user_rf.apply(lambda row: get_user_segment(row['R等级'], row['F等级']), axis=1)

# ---------------------- 4. 输出结果 ----------------------
print("="*80)
print("📊 用户分层结果（前10行）")
print("="*80)
print(user_rf.head(10).to_string(index=False))

print("\n" + "="*80)
print("📊 各分层用户数量统计")
print("="*80)
segment_count = user_rf['用户分层'].value_counts()
print(segment_count)

# ---------------------- 5. 导出Excel ----------------------
user_rf.to_excel('用户分层结果.xlsx', index=False, engine='openpyxl')

# ---------------------- 6. 可视化分层占比 ----------------------
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

plt.figure(figsize=(10, 6))
segment_count.plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
plt.title('用户分层占比', fontsize=16, fontweight='bold')
plt.ylabel('')
plt.tight_layout()
plt.savefig('用户分层饼图.png', dpi=300)
plt.show()

print("\n 运行完成！")
print(" 已导出：用户分层结果.xlsx")
print(" 已生成：用户分层饼图.png")
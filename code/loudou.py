import pandas as pd
import matplotlib.pyplot as plt

# ---------------------- 1. 读取数据并查看结构 ----------------------
df = pd.read_csv('data_cleaned.csv')

# 打印所有列名，确认关键列
print("=== 数据列名 ===")
print(df.columns.tolist())

# 打印行为列的所有唯一值（如果存在）
print("\n=== 各列的唯一值（方便你找行为列） ===")
for col in df.columns:
    print(f"{col}: {df[col].unique()[:5]}...")  # 只打印前5个值

# ---------------------- 2. 手动指定你数据里的关键列 ----------------------
# 从你之前的截图，我们已经确认了这些列：
user_col = 'user_id'       # 用户ID
# 👇 这里你可以手动改成你数据里的行为列名
behavior_col = 'behavior_type'  # 常见电商数据列名，也可能叫 'behavior' / 'action' / 'type'

# 👇 这里改成你数据里的行为值（如果是英文，比如 pv/fav/cart/buy）
browse_value = 'pv'    # 浏览
fav_value    = 'fav'   # 收藏
cart_value   = 'cart'  # 加购
buy_value    = 'buy'   # 购买

# ---------------------- 3. 统计各环节独立用户数 ----------------------
# 先检查行为列是否存在
if behavior_col not in df.columns:
    print(f"\n❌ 错误：数据中没有 '{behavior_col}' 列！请根据上面的列名列表修改 behavior_col")
else:
    # 统计各环节用户数
    browse_users = df[df[behavior_col] == browse_value][user_col].nunique()
    fav_users    = df[df[behavior_col] == fav_value][user_col].nunique()
    cart_users   = df[df[behavior_col] == cart_value][user_col].nunique()
    buy_users    = df[df[behavior_col] == buy_value][user_col].nunique()

    # 构建漏斗数据
    funnel_data = pd.DataFrame({
        '环节': ['浏览', '收藏', '加购', '购买'],
        '用户数': [browse_users, fav_users, cart_users, buy_users]
    })

    # ---------------------- 4. 计算转化率 ----------------------
    if browse_users > 0:  # 避免除以0
        # 环节转化率（上一步到下一步）
        funnel_data['环节转化率'] = funnel_data['用户数'] / funnel_data['用户数'].shift(1)
        # 整体转化率（相对于浏览）
        funnel_data['整体转化率'] = funnel_data['用户数'] / browse_users

        # 格式化百分比
        funnel_data['环节转化率'] = funnel_data['环节转化率'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "—")
        funnel_data['整体转化率'] = funnel_data['整体转化率'].apply(lambda x: f"{x:.2%}")
    else:
        print("\n❌ 错误：浏览用户数为0，请检查行为值是否正确！")

    # ---------------------- 5. 输出结果 ----------------------
    print("\n" + "="*80)
    print("📊 电商全流程漏斗转化分析（独立用户数）")
    print("="*80)
    print(funnel_data.to_string(index=False))

    # 导出Excel
    funnel_data.to_excel('电商漏斗转化分析.xlsx', index=False, engine='openpyxl')

    # ---------------------- 6. 绘制正确的漏斗图 ----------------------
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    plt.figure(figsize=(10, 6))
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    bars = plt.bar(funnel_data['环节'], funnel_data['用户数'], color=colors, alpha=0.8)

    # 在柱子上标注用户数 + 转化率
    for i, (idx, row) in enumerate(funnel_data.iterrows()):
        user_cnt = row['用户数']
        rate = row['整体转化率']
        plt.text(i, user_cnt + max(funnel_data['用户数'])*0.01,
                 f"{user_cnt:,}\n{rate}",
                 ha='center', fontsize=12, fontweight='bold')

    plt.title('电商用户行为漏斗转化图', fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('独立用户数', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('电商漏斗转化图.png', dpi=300)
    plt.show()

    print("\n✅ 分析完成！")
    print("📁 已导出：电商漏斗转化分析.xlsx")
    print("📊 已生成：电商漏斗转化图.png")
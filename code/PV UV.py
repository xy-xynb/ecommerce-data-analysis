import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 读取 CSV 文件
df = pd.read_csv("data_cleaned.csv")

# 将 date 字段转换为日期格式
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# 统计每日 PV
# PV 指 behavior_type 为 pv 的行为数量
daily_pv = df[df["behavior_type"] == "pv"].groupby("date").size()
daily_pv.name = "PV"

# 统计每日 UV
# UV 指每天去重后的用户数量
daily_uv = df.groupby("date")["user_id"].nunique()
daily_uv.name = "UV"

# 合并 PV 和 UV
daily_stats = pd.concat([daily_pv, daily_uv], axis=1).fillna(0)

# 绘制折线图
plt.figure(figsize=(12, 6))

plt.plot(
    daily_stats.index,
    daily_stats["PV"],
    marker="o",
    label="PV"
)

plt.plot(
    daily_stats.index,
    daily_stats["UV"],
    marker="s",
    label="UV"
)

plt.title("每日 PV 与 UV")
plt.xlabel("日期")
plt.ylabel("数量")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
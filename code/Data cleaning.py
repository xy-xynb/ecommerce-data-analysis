import pandas as pd

# ==========================
# 1. 读取数据
# ==========================
# 假设你的数据文件为 CSV 格式
df = pd.read_csv("ecommerce_user_behavior_simulated_50000.csv")

# 查看前几行数据，了解字段情况
print(df.head())

# ==========================
# 2. 缺失值处理
# ==========================
# 检查每列缺失值情况
print(df.isnull().sum())

# 对关键字段（如 user_id, item_id, behavior_time）缺失值直接删除
df = df.dropna(subset=['user_id', 'item_id', 'behavior_time'])

# 对价格字段缺失值可用中位数填充（根据业务逻辑可调整）
df['price'] = df['price'].fillna(df['price'].median())

# 对 category_id 或 behavior_type 可以用默认值填充（如-1或'unknown'）
df['category_id'] = df['category_id'].fillna(-1)
df['behavior_type'] = df['behavior_type'].fillna('unknown')

# ==========================
# 3. 重复值处理
# ==========================
# 查看重复行
print("重复行数:", df.duplicated().sum())

# 删除完全重复的行
df = df.drop_duplicates()

# ==========================
# 4. 时间格式转换
# ==========================
# 将 behavior_time 转为 datetime 类型
df['behavior_time'] = pd.to_datetime(df['behavior_time'], errors='coerce')

# 将无法转换的时间设为缺失值并删除
df = df.dropna(subset=['behavior_time'])

# ==========================
# 5. 提取日期和小时字段
# ==========================
# 提取日期（年月日）
df['date'] = df['behavior_time'].dt.date

# 提取小时
df['hour'] = df['behavior_time'].dt.hour

# ==========================
# 6. 检查最终数据
# ==========================
print(df.info())
print(df.head())

# ==========================
# 7. 保存清洗后的数据（可选）
# ==========================
df.to_csv("data_cleaned.csv", index=False)
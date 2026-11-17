# CSV 数据清洗练习

## 已下载：Titanic

- 文件：`raw/titanic.csv`
- 来源：https://github.com/mwaskom/seaborn-data/blob/master/titanic.csv
- 原始下载：https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv
- 获取日期：2026-11-13
- 保留下载原文，没有人为添加错误。
- 规模：891 行、15 列，不含表头。
- 空值：age 177 个，embarked 2 个，deck 688 个，embark_town 2 个。
- 全字段相同的重复行：107 行。数据不包含唯一乘客 ID，同样的属性可能对应不同乘客，不能直接认定为重复采集并删除。

## 第一轮练习

在项目根目录运行以下代码（或保存到自己的练习脚本）：

```python
import pandas as pd

df = pd.read_csv("data/raw/titanic.csv")
print(df.head())
df.info()
print(df.isna().sum())
print("相同行数：", df.duplicated().sum())
print(df.describe(include="all"))

clean = df.copy()
# 入门练习：用年龄中位数填补。真实建模时只用训练集计算中位数。
clean["age_missing"] = clean["age"].isna()
clean["age"] = clean["age"].fillna(clean["age"].median())
# 保留原列，以免丢失缺失模式；新增供分组展示的分类列。
clean["deck_group"] = clean["deck"].fillna("Unknown")

print(clean.groupby("sex")["survived"].mean())
print(clean.groupby("pclass")["fare"].median())
clean.to_csv("data/titanic_cleaned.csv", index=False)
```

自行完成：

1. 计算各列缺失率，解释为什么 deck 不适合随意用众数补齐。
2. 查看 embarked 与 embark_town 的对应关系，确定一致的缺失值处理方式。
3. 检查年龄是否为负数、票价是否为负数，并研究票价为 0 的记录；异常候选不等于错误。
4. 比较不同舱位、性别的生存率，注意分组样本量。
5. 画年龄直方图和不同舱位的票价箱线图。
6. 保存清洗后的文件，记录每一步处理原因；保留 raw 下的原始文件。

## 其他推荐 CSV（尚未下载）

### Penguins：企鹅测量数据

- 原始下载：https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv
- 练习方向：检查缺失值、数值类型，按物种和岛屿分组统计，绘制散点图。
- 字段与来源说明：https://github.com/mwaskom/seaborn-data

### Taxis：出租车行程数据

- 原始下载：https://raw.githubusercontent.com/mwaskom/seaborn-data/master/taxis.csv
- 练习方向：解析 pickup/dropoff 时间，检查结束时间是否早于开始时间、费用是否合理；按小时统计订单量，检查分类列缺失值。
- 字段与来源说明：https://github.com/mwaskom/seaborn-data

下载后放入 `data/raw/`。使用前检查来源仓库与原始数据集的许可和说明。

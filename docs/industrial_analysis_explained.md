# 工业故障分析脚本：逐行讲解

对应文件：`industrial_analysis.py`。本文使用当前脚本的实际行号；以后修改脚本，行号可能变化。

这个脚本做数据检查和探索分析，还没有训练故障诊断模型。它不会自动下载真实数据。

## 先理解运行顺序

1. 导入依赖，创建列名列表，定义三个函数。
2. 文件末尾调用 `main()`。
3. `main()` 解析参数，选择教学数据或读取 CSV。
4. `analyze()` 规范数据、生成质量标记、统计、保存文件并绘图。

`raw` 是原始表，`clean` 是规范后的完整副本，`quality` 是逐行质量标记，`usable` 是暂时通过检查的统计子集，`by_type` 是分组结果。

Python 用缩进表示代码归属。空白行只用于排版，不执行；下面逐行讲解所有非空行。仅包含括号的行也列出，以便理解跨行语句。

## 逐行对照

### 第 1 行

```python
"""AI4I 工业故障数据入门：检查质量、统计故障率、绘图。
```

开始模块说明字符串（三个双引号）。这段文字说明脚本用途，不是业务计算。

### 第 3 行

```python
真实数据：python industrial_analysis.py
```

说明默认运行命令：不加参数时读取真实 AI4I CSV。这行在说明字符串内部，不会作为 Python 命令执行。

### 第 4 行

```python
教学演示：python industrial_analysis.py --demo
```

说明演示命令：加 --demo 后使用程序构造的教学数据，不需要下载 CSV。

### 第 5 行

```python
指定文件：python industrial_analysis.py --input /path/to/ai4i2020.csv
```

说明如何通过 --input 指定 CSV 路径。/path/to/ 是占位示例，需要换成实际路径。

### 第 6 行

```python
"""
```

结束模块说明字符串。整段说明可通过 __doc__ 获取。

### 第 8 行

```python
import argparse
```

导入 Python 标准库 argparse，用于读取终端里的 --input、--output、--demo 等参数。

### 第 9 行

```python
from pathlib import Path
```

从标准库 pathlib 导入 Path 类，用对象表示文件和目录路径，避免手工拼接路径字符串。

### 第 11 行

```python
import pandas as pd
```

导入第三方库 pandas，并起别名 pd。后面的 pd.read_csv、pd.DataFrame 都来自它。

### 第 14 行

```python
ROOT = Path(__file__).resolve().parent
```

__file__ 是当前脚本文件的位置；Path(...) 将其变成路径对象；resolve() 得到解析后的绝对路径；parent 取所在目录。ROOT 因此是脚本所在目录，与终端当前所在目录不一定相同。大写名称表示约定上的常量，Python 不强制禁止修改。

### 第 15 行

```python
FEATURES = [
```

开始定义 FEATURES 列表，用来统一保存五个数值特征的列名。列表用方括号，元素按顺序保存。

### 第 16 行

```python
    "Air temperature [K]",
```

空气温度列名，单位 K（开尔文）。字符串必须与 CSV 的表头完全一致，包括空格和方括号。

### 第 17 行

```python
    "Process temperature [K]",
```

工艺温度列名，单位 K。

### 第 18 行

```python
    "Rotational speed [rpm]",
```

转速列名，单位 rpm，即每分钟转数。

### 第 19 行

```python
    "Torque [Nm]",
```

扭矩列名，单位 Nm，即牛顿米。

### 第 20 行

```python
    "Tool wear [min]",
```

刀具磨损列名，单位 min。它用磨损累计时间表示这个特征，不是振动幅值。

### 第 21 行

```python
]
```

结束 FEATURES 列表。最后一个元素后的逗号可以保留，方便继续添加元素。

### 第 22 行

```python
LABELS = ["Machine failure", "TWF", "HDF", "PWF", "OSF", "RNF"]
```

定义标签列名：Machine failure 是总体故障标记；TWF 为刀具磨损故障，HDF 为散热故障，PWF 为功率故障，OSF 为过应变故障，RNF 为随机故障。0 表示未标记，1 表示标记；这些故障类型并不互斥。

### 第 23 行

```python
REQUIRED = ["UDI", "Product ID", "Type", *FEATURES, *LABELS]
```

构造必需字段列表。*FEATURES 和 *LABELS 在列表中表示展开元素，不是乘法。例如 ["a", *["b", "c"]] 得到 ["a", "b", "c"]。UDI 是记录标识，Product ID 是产品标识，Type 是质量类型。

### 第 26 行

```python
def make_demo_data():
```

定义函数 make_demo_data。def 只创建函数，此时还不执行函数体。后面缩进的内容属于该函数。函数名后的空括号表示它不要求输入参数。

### 第 27 行

```python
    """少量人为构造的教学记录，不代表真实设备或 AI4I 的统计规律。"""
```

函数说明字符串，强调演示记录是人为构造的数据，不能用来研究真实设备规律。

### 第 28 行

```python
    rows = []
```

创建空列表 rows，用来逐条收集记录；每条记录将是一个字典。

### 第 29 行

```python
    for i in range(12):
```

循环 12 次，i 依次为 0 到 11。range(12) 不包含 12，冒号后的缩进代码属于循环。

### 第 30 行

```python
        failed = int(i in (3, 9))
```

i in (3, 9) 判断 i 是否为 3 或 9，结果是 True/False；int(...) 把它转换为 1/0。因此只有这两条记录被设为故障。

### 第 31 行

```python
        rows.append({
```

开始创建字典，并通过 rows.append(...) 把它追加到列表。字典中每一项是“列名: 值”。

### 第 32 行

```python
            "UDI": i + 1,
```

将 UDI 设为 i + 1，生成 1 到 12 的标识。

### 第 33 行

```python
            "Product ID": f"DEMO{i + 1:03d}",
```

f 字符串把表达式放进文本；i + 1:03d 表示按十进制整数输出，至少三位，不足补零。例如 i=0 时得到 DEMO001。

### 第 34 行

```python
            "Type": ["L", "M", "H"][i % 3],
```

先创建 L、M、H 三个字符串组成的列表，再用 i % 3 的余数作为下标。余数循环为 0、1、2，所以类型循环为 L、M、H。Python 列表下标从 0 开始。

### 第 35 行

```python
            "Air temperature [K]": 298 + i * 0.2,
```

生成空气温度：298 + i×0.2。例如第一条为 298.0 K，第二条为 298.2 K。

### 第 36 行

```python
            "Process temperature [K]": 308 + i * 0.2,
```

生成工艺温度：308 + i×0.2。

### 第 37 行

```python
            "Rotational speed [rpm]": 1450 + i * 25,
```

生成转速：1450 + i×25 rpm。这种简单规律只用于展示程序流程。

### 第 38 行

```python
            "Torque [Nm]": 30 + i * 2,
```

生成扭矩：30 + i×2 Nm。

### 第 39 行

```python
            "Tool wear [min]": i * 18,
```

生成刀具磨损时间：i×18 min。

### 第 40 行

```python
            "Machine failure": failed,
```

把总体故障列设为本轮循环计算的 failed，也就是 0 或 1。

### 第 41 行

```python
            "TWF": failed,
```

为简化演示，把刀具磨损故障列也设为 failed。这不表示真实数据中所有故障都由刀具磨损造成。

### 第 42 行

```python
            "HDF": 0, "PWF": 0, "OSF": 0, "RNF": 0,
```

同一物理行中写了四个字典项，把其余四种故障标记全部设为 0。

### 第 43 行

```python
        })
```

} 结束字典，) 结束 append 调用。至此完成一条记录；循环会继续创建下一条。

### 第 44 行

```python
    rows[1]["Type"] = " m "
```

修改列表中第 2 条记录的 Type，故意写成带前后空格的小写字符串，用来练习 strip 和 upper。此行已退出 for 循环。

### 第 45 行

```python
    rows[2]["Torque [Nm]"] = None
```

将第 3 条记录的扭矩设为 None，表示没有提供值；构成 DataFrame 后，数值列里通常显示为 NaN。

### 第 46 行

```python
    rows[4]["Rotational speed [rpm]"] = "unknown"
```

将第 5 条记录的转速设为字符串 unknown，故意制造“本应为数值却出现文本”的问题。

### 第 47 行

```python
    rows[5]["Tool wear [min]"] = -5
```

将第 6 条记录的磨损时间设为 -5，故意制造不合理的负数。

### 第 48 行

```python
    rows[6]["Machine failure"] = 2
```

将第 7 条记录的总体故障标记设为 2；该字段只允许 0/1，因此这是非法标签。

### 第 49 行

```python
    rows[7]["Type"] = "X"
```

将第 8 条记录的类型设为 X，而本例的允许值只有 L/M/H。

### 第 50 行

```python
    rows.append(rows[0].copy())
```

复制第 1 条记录并追加到末尾，制造完整重复记录。copy() 创建新的字典，避免两条记录共享同一字典对象。现在列表共有 13 条记录。

### 第 51 行

```python
    return pd.DataFrame(rows)
```

用字典列表创建 DataFrame：字典键成为列名，每个字典成为一行。return 把表格返回给调用者，并结束函数。

### 第 54 行

```python
def analyze(raw, output_dir, demo=False):
```

定义核心函数 analyze：raw 是原始 DataFrame；output_dir 是输出目录 Path 对象；demo 是是否演示的标记，默认 False。

### 第 55 行

```python
    missing_columns = sorted(set(REQUIRED) - set(raw.columns))
```

把必需列名和实际列名分别变成集合，用集合差集找出缺少的字段，再 sorted 排序。例如必需 A、B，实际只有 A，结果为 ["B"]。

### 第 56 行

```python
    if missing_columns:
```

非空列表在 if 中视为 True。如果确实缺少字段，就执行下一行。

### 第 57 行

```python
        raise ValueError(f"CSV 缺少必要字段：{missing_columns}")
```

主动抛出 ValueError，说明输入数据结构不符合要求。f 字符串会把缺少字段列表放进报错信息。后面的分析不会继续执行。

### 第 58 行

```python
    if raw.empty:
```

raw.empty 判断表格是否为空；在前面已确认有必需列的前提下，这里用于检查是否没有数据行。

### 第 59 行

```python
        raise ValueError("CSV 没有数据行。")
```

没有记录时抛出 ValueError，避免继续做没有意义的统计。

### 第 61 行

```python
    output_dir.mkdir(parents=True, exist_ok=True)
```

创建输出目录。parents=True 允许一并创建缺少的上级目录；exist_ok=True 表示目录已存在时不报错。

### 第 62 行

```python
    clean = raw.copy()
```

复制原始 DataFrame，把工作副本命名为 clean。后续赋值修改 clean，不直接修改 raw 或原始 CSV 文件。

### 第 63 行

```python
    # 保留原始文件；只在副本中规范字段，不直接删除可疑记录。
```

注释，解释清洗原则。# 后面的文字不会执行。

### 第 64 行

```python
    for column in ["Type", "Product ID"]:
```

遍历 Type 和 Product ID 两个文本列；column 每轮保存其中一个列名。

### 第 65 行

```python
        clean[column] = clean[column].astype("string").str.strip()
```

clean[column] 取出这一列；astype("string") 使用 Pandas 可空字符串类型；str.strip() 对每个非空字符串去掉两端空白。赋值后替换工作副本中的该列。

### 第 66 行

```python
        clean[column] = clean[column].replace("", pd.NA)
```

把去除空白后的空字符串替换为 Pandas 的缺失值 pd.NA。它与字符串 "NA" 不同，也与数值 0 不同。

### 第 67 行

```python
    clean["Type"] = clean["Type"].str.upper()
```

把 Type 的文本转换为大写，例如 "m" 变成 "M"，实现类别格式统一。

### 第 69 行

```python
    quality = pd.DataFrame(index=raw.index)
```

创建质量标记表 quality，行索引与原始表一致，暂时没有列。索引一致使后续按行关联数据更可靠。

### 第 70 行

```python
    quality["source_record"] = range(1, len(raw) + 1)
```

添加 source_record 列，从 1 编号到数据行数。len(raw) 是行数；range 的结束值不包含，因此使用 len(raw)+1。这是数据记录号，不保证等于 CSV 的物理文本行号。

### 第 71 行

```python
    quality["duplicate_full_row"] = raw.duplicated(keep=False)
```

检查原始表的整行重复。keep=False 会把重复组中的所有行都标为 True，包含第一条，不只是后来的重复项。使用 raw 意味着是在文本规范化前检查。

### 第 72 行

```python
    quality["missing_product_id"] = clean["Product ID"].isna()
```

isna() 逐行判断产品标识是否缺失，结果是一列布尔值，写入质量标记表。

### 第 73 行

```python
    for column in ["UDI", *FEATURES, *LABELS]:
```

遍历 UDI、五个特征和六个标签，对它们统一做数值转换。* 仍是列表展开。

### 第 74 行

```python
        clean[column] = pd.to_numeric(clean[column], errors="coerce")
```

pd.to_numeric 尝试转换数值；errors="coerce" 表示无法转换的内容变成 NaN，而不是立即报错。例如 unknown 会变成 NaN。

### 第 75 行

```python
        quality[f"missing_or_non_numeric: {column}"] = clean[column].isna()
```

检查转换后的缺失值，并以动态列名记录。原来就缺失和转换失败都会在这里被标记；该标记没有进一步区分这两种原因。

### 第 77 行

```python
    quality["duplicate_udi"] = (
```

开始计算 duplicate_udi 标记。左括号允许表达式跨多行书写，不需要反斜杠续行。

### 第 78 行

```python
        clean["UDI"].notna() & clean["UDI"].duplicated(keep=False)
```

notna() 要求 UDI 不缺失；duplicated(keep=False) 判断它是否重复。& 对两列布尔值逐元素做“且”，因此只标记非空且重复的 UDI。

### 第 79 行

```python
    )
```

结束跨行表达式，并完成 duplicate_udi 列的赋值。

### 第 80 行

```python
    quality["invalid_udi"] = (
```

开始计算 invalid_udi，检查记录标识是否为正整数。

### 第 81 行

```python
        clean["UDI"].isna() | clean["UDI"].le(0) | clean["UDI"].mod(1).ne(0)
```

isna() 检查缺失；le(0) 表示 <=0；mod(1) 求除以 1 的余数，再 ne(0) 判断余数不为 0，即不是整数。| 是逐元素“或”，满足任一条件即不合法。

### 第 82 行

```python
    )
```

结束 invalid_udi 的计算。

### 第 83 行

```python
    quality["invalid_type"] = ~clean["Type"].isin(["L", "M", "H"])
```

isin(["L", "M", "H"]) 检查类型是否在允许集合中；前面的 ~ 将布尔值逐元素取反，因此不在允许集合中的类型被标记。

### 第 84 行

```python
    for column in LABELS:
```

逐个遍历故障标签列。

### 第 85 行

```python
        quality[f"invalid_label: {column}"] = ~clean[column].isin([0, 1])
```

每个标签只允许 0 或 1。isin 检查合法值，~ 取反后标记非法标签；缺失值也会被标记为非法。

### 第 86 行

```python
    for column in FEATURES:
```

逐个遍历五个数值特征，检查简单的取值范围。

### 第 87 行

```python
        # 这里只检查基础物理范围。数值极端可能与故障有关，不自动删除。
```

注释提醒：这里只做基础检查，不能把罕见或极端数值直接当成错误。

### 第 88 行

```python
        invalid = clean[column].lt(0)
```

lt(0) 表示逐元素小于 0。先把所有特征的负数标记为非法，暂存在 invalid 中。

### 第 89 行

```python
        if column in FEATURES[:3]:
```

FEATURES[:3] 取列表前 3 个元素，即两种温度和转速。这里给这三个字段应用更严格的示例规则。

### 第 90 行

```python
            invalid = clean[column].le(0)
```

对温度与转速，改为 le(0)，即小于或等于 0 都标记。温度单位是 K；转速为 0 也可能表示停机，因此这是本练习对 AI4I 运行工况的检查规则，不是所有工业场景的通用规则。

### 第 91 行

```python
        quality[f"invalid_range: {column}"] = invalid | clean[column].isin(
```

把范围错误与无穷值检查结果用 | 合并，保存到对应特征的质量标记列。isin 调用在下一行提供参数。

### 第 92 行

```python
            [float("inf"), float("-inf")]
```

创建正无穷和负无穷两个浮点值组成的列表，用于检测数值列中的非有限值。缺失值已在前面的 isna 中检查。

### 第 93 行

```python
        )
```

关闭 isin 的括号，结束这条跨行赋值语句。

### 第 95 行

```python
    # 新增摄氏温度列，保留原始 K 单位字段。
```

注释说明：保留原有 K 列，另建摄氏温度列，不把单位和数值混淆。

### 第 96 行

```python
    clean["Air temperature [C]"] = clean["Air temperature [K]"] - 273.15
```

对整列空气温度减去 273.15，转换为摄氏度，新增 Air temperature [C]。整列运算不需要手动循环每一行。

### 第 97 行

```python
    clean["Process temperature [C]"] = clean["Process temperature [K]"] - 273.15
```

同样把工艺温度转换为摄氏度，并保存到新列。

### 第 98 行

```python
    clean["needs_review"] = quality.drop(columns="source_record").any(axis=1)
```

先从临时检查视图中去掉 source_record，避免数字编号参与布尔判断；any(axis=1) 按行检查是否至少有一个 True，将结果写为 needs_review。drop 不会在这里修改原 quality 表。

### 第 100 行

```python
    # 统计仅使用通过上述基础检查的记录；其余记录仍保存在清洗结果中。
```

注释说明统计范围：检查未通过的数据仍保留在 clean 中，只是不进入后面的故障率统计。

### 第 101 行

```python
    usable = clean.loc[~clean["needs_review"]].copy()
```

~clean["needs_review"] 选出不需要复核的行；loc[...] 按布尔条件筛选；copy() 创建独立统计副本 usable。这里的“通过”仅代表通过本脚本的基础规则，不保证数据完全正确。

### 第 102 行

```python
    by_type = usable.groupby("Type")["Machine failure"].agg(
```

按 Type 分组，只选择 Machine failure 列，调用 agg 同时计算多种统计量。

### 第 103 行

```python
        sample_count="count", failure_count="sum", failure_rate="mean"
```

命名聚合：count 计算非空样本数，sum 把 0/1 标签求和得到故障数，mean 求平均得到故障率。例如 [0,1,0,1] 的平均数是 0.5，即 50%。

### 第 104 行

```python
    )
```

结束 agg 调用。by_type 的行索引是类型，列是上述三个命名统计量。

### 第 106 行

```python
    clean.to_csv(output_dir / "cleaned.csv", index=False, encoding="utf-8-sig")
```

把全部处理后的记录保存为 cleaned.csv；index=False 不保存 Pandas 行索引；utf-8-sig 为 UTF-8 加 BOM，便于一些表格软件识别中文。Path 的 / 运算符在这里拼接路径，不是数值除法。

### 第 107 行

```python
    quality.to_csv(output_dir / "quality_flags.csv", index=False, encoding="utf-8-sig")
```

保存逐行质量标记表 quality_flags.csv，同样不额外写入行索引。source_record 可用于对应原始记录。

### 第 108 行

```python
    by_type.to_csv(output_dir / "failure_by_type.csv", encoding="utf-8-sig")
```

保存分组统计。这里没有 index=False，默认保留索引，因此 Type 也会写入 CSV，避免丢失类型信息。

### 第 109 行

```python
    clean[FEATURES].describe().to_csv(output_dir / "numeric_summary.csv")
```

选取 clean 中五个特征列，用 describe 计算数量、均值、标准差、最小值、四分位数和最大值，再保存。注意这里用的是 clean，而非 usable，因此仍包含已标记的非法范围值，适合检查数据，不能直接当成最终有效样本统计。NaN 通常不参与这些数值统计。

### 第 111 行

```python
    report = [
```

开始建立 report 字符串列表，逐项组装文本报告。

### 第 112 行

```python
        "【教学合成演示数据】" if demo else "AI4I 数据检查报告",
```

条件表达式：demo 为 True 时使用教学标记，否则使用 AI4I 报告标题。写法为“真时的值 if 条件 else 假时的值”。

### 第 113 行

```python
        f"输入记录数：{len(raw)}",
```

把原始记录数嵌入报告文本。

### 第 114 行

```python
        f"需人工检查的记录数：{int(clean['needs_review'].sum())}",
```

对 needs_review 的布尔值求和，True 计作 1，得到需要复核的行数；int(...) 把结果转换为整数用于展示。

### 第 115 行

```python
        f"用于故障率统计的记录数：{len(usable)}",
```

记录真正进入分组统计的 usable 行数。

### 第 116 行

```python
        "同一记录可能触发多种质量标记，标记次数不能直接相加作为行数。",
```

解释标记次数与问题行数的区别：同一行可同时缺失、类别非法，不能把不同标记数量相加当作总问题行数。

### 第 117 行

```python
        "重复标记覆盖重复组内全部记录；统计暂时排除整组，待核实后再决定保留哪条。",
```

解释本脚本对重复记录的保守策略：整组先排除统计，等待核实，而不是立即删除或任选一条。

### 第 118 行

```python
        "未填补缺失值、未删除原始记录、未自动删除极端值。",
```

说明实际处理边界：没有自动补值、删行或移除极端值。但数值转换失败的文本已在副本中变为 NaN；原始数据仍保留。

### 第 119 行

```python
        "清洗统计可能改变样本分布，分析时应核实被排除的记录。",
```

提醒排除问题记录后，统计结果可能有选择偏差。

### 第 120 行

```python
        "演示数据不用于推断真实设备故障规律。" if demo else "",
```

演示模式追加警示语；真实文件模式追加空字符串，join 后只会产生一个空白行。

### 第 121 行

```python
        "\n各项质量标记数量：",
```

添加质量标记段落标题。字符串中的 \n 表示换行字符。

### 第 122 行

```python
        quality.drop(columns="source_record").sum().to_string(),
```

去掉记录编号后，对每个布尔标记列求和，统计该类问题涉及的记录数量；to_string() 将结果转换为便于打印的文本。默认按列求和，即 axis=0。

### 第 123 行

```python
        "\n原始数据缺失值：",
```

添加原始缺失值段落标题。

### 第 124 行

```python
        raw.isna().sum().to_string(),
```

对原始 raw 先逐单元格检查是否缺失，再按列求和并转成文本。由于使用 raw，unknown 等非空文本不会算作原始缺失，转换失败另见质量标记。

### 第 125 行

```python
        "\n按设备类型统计：",
```

添加按设备类型统计的段落标题。

### 第 126 行

```python
        by_type.to_string(),
```

把分组统计表转换为纯文本，放入报告列表。

### 第 127 行

```python
    ]
```

结束报告列表。

### 第 128 行

```python
    report_text = "\n".join(report)
```

用换行字符把列表中的所有字符串连接起来，得到完整 report_text。

### 第 129 行

```python
    (output_dir / "report.txt").write_text(report_text, encoding="utf-8")
```

拼接 report.txt 的路径，再用 UTF-8 将文本写入文件。文件不存在会创建，存在则覆盖。

### 第 130 行

```python
    print(report_text)
```

把相同报告打印到终端，方便运行时查看。

### 第 132 行

```python
    if not usable.empty:
```

检查 usable 是否非空。not 把单个布尔值取反；只有存在可统计记录才尝试绘图。

### 第 133 行

```python
        import matplotlib
```

在真正需要绘图时导入 Matplotlib，而不是程序启动时就加载它。这样 --help 等路径不必建立绘图环境。

### 第 135 行

```python
        # 使用非交互式绘图，图片保存到文件，无需弹出窗口。
```

注释说明采用非交互模式，适合命令行和无图形桌面的运行环境。

### 第 136 行

```python
        matplotlib.use("Agg")
```

选择 Agg 后端，把图画到图片文件；它不弹出窗口。该配置应在导入 pyplot 之前设置。

### 第 137 行

```python
        import matplotlib.pyplot as plt
```

导入 Matplotlib 的 pyplot 接口并命名为 plt。

### 第 139 行

```python
        fig, axes = plt.subplots(1, 2, figsize=(11, 4))
```

创建 1 行、2 列的子图；fig 是整张图，axes 是两个绘图区组成的数组；figsize=(11,4) 的单位是英寸。逗号左侧的写法是同时接收两个返回值。

### 第 140 行

```python
        (by_type["failure_rate"] * 100).plot.bar(ax=axes[0], rot=0)
```

把 0～1 的故障率乘以 100，调用 Pandas 绘图接口画柱状图。ax=axes[0] 放到左图；rot=0 让横轴标签保持水平。

### 第 141 行

```python
        axes[0].set(title="Failure rate by type", xlabel="Type", ylabel="Failure rate (%)")
```

设置左图标题、横轴名称和纵轴名称。图中用英文可减少中文字体缺失的问题。

### 第 142 行

```python
        for label, group in usable.groupby("Machine failure"):
```

按总体故障标签分组。每轮获得 label（0 或 1）以及对应记录组成的 group，分别画正常和故障样本。

### 第 143 行

```python
            axes[1].scatter(
```

调用右图的 scatter 方法，开始绘制散点图。

### 第 144 行

```python
                group["Rotational speed [rpm]"], group["Torque [Nm]"],
```

第一个参数提供横坐标转速，第二个参数提供纵坐标扭矩；同一行的两个数值构成一个点。

### 第 145 行

```python
                label="Failure" if label == 1 else "Normal", alpha=0.6, s=18,
```

label 设置图例文字，1 对应 Failure，否则 Normal；alpha=0.6 设置透明度；s=18 设置点的标记面积，单位是平方磅。

### 第 146 行

```python
            )
```

结束 scatter 调用。循环会为另一个标签继续添加散点。

### 第 147 行

```python
        axes[1].set(xlabel="Speed (rpm)", ylabel="Torque (Nm)")
```

设置右图的横纵轴名称，明确 rpm 和 Nm 单位。

### 第 148 行

```python
        axes[1].legend()
```

显示图例，读取 scatter 中设置的 label。

### 第 149 行

```python
        if demo:
```

判断是否使用教学数据。

### 第 150 行

```python
            fig.suptitle("SYNTHETIC TEACHING DEMO")
```

为整张图添加教学合成数据标题，避免把示意结果误认为真实数据分析结论。

### 第 151 行

```python
        fig.tight_layout()
```

自动调整子图间距，减少标题、坐标名称等元素相互遮挡。

### 第 152 行

```python
        fig.savefig(output_dir / "overview.png", dpi=150)
```

保存 overview.png，dpi=150 表示每英寸 150 个像素。默认重复运行会覆盖同一路径的图片。

### 第 153 行

```python
        plt.close(fig)
```

关闭这张图，释放绘图资源；它不会删除已保存的图片。

### 第 154 行

```python
    else:
```

对应第 132 行的 if：如果没有通过基础检查的记录，就进入这个分支。

### 第 155 行

```python
        print("没有通过基础检查的记录，跳过绘图。")
```

打印跳过绘图的原因。CSV 与文本报告仍已在此前保存。

### 第 156 行

```python
    print(f"\n结果已保存到：{output_dir}")
```

打印输出目录。此行缩进已退出绘图 if/else，因此两种情况都会执行。

### 第 159 行

```python
def main():
```

定义 main 函数，用于组织参数解析、读取输入和调用分析流程。

### 第 160 行

```python
    parser = argparse.ArgumentParser(description=__doc__)
```

创建命令行参数解析器。description=__doc__ 使用文件开头的说明字符串作为 --help 帮助内容。

### 第 161 行

```python
    parser.add_argument("--input", type=Path, default=ROOT / "data/raw/ai4i2020.csv")
```

注册 --input 参数；type=Path 将用户输入转成 Path 对象；未提供时默认使用脚本目录下的 data/raw/ai4i2020.csv。

### 第 162 行

```python
    parser.add_argument("--output", type=Path, help="自定义输出目录")
```

注册 --output 参数。用户不提供时默认 None，后面再决定输出位置。help 文本出现在 --help 中。

### 第 163 行

```python
    parser.add_argument("--demo", action="store_true", help="使用人为构造的教学记录")
```

注册 --demo 开关。action="store_true" 表示写了该开关就是 True，没写就是 False，不需要再跟一个值。

### 第 164 行

```python
    args = parser.parse_args()
```

读取并解析实际命令行参数，返回 Namespace 对象 args。之后可以用 args.input、args.demo 等属性读取结果。

### 第 165 行

```python
    if args.demo:
```

如果传入了 --demo，进入演示分支。

### 第 166 行

```python
        raw = make_demo_data()
```

调用 make_demo_data，接收返回的 DataFrame，并命名为 raw。这时才真正执行第 26 行定义的函数。

### 第 167 行

```python
    else:
```

否则使用真实文件输入。若 --demo 与 --input 同时传入，本脚本仍优先执行演示分支。

### 第 168 行

```python
        if not args.input.is_file():
```

is_file() 判断输入路径是否为已存在的普通文件；not 表示不存在文件时进入下面的错误处理。

### 第 169 行

```python
            parser.exit(1, f"未找到 CSV：{args.input}\n请下载 AI4I 数据，或先运行：python industrial_analysis.py --demo\n")
```

以退出码 1 结束程序，打印缺失文件路径及演示命令。0 通常表示成功，非 0 表示失败。脚本不在这里自动联网下载。

### 第 170 行

```python
        raw = pd.read_csv(args.input)
```

用 Pandas 读取 CSV 为 DataFrame。默认把第一行当作列名，并尝试推断类型与识别常见缺失值。

### 第 171 行

```python
    output_dir = args.output or ROOT / "outputs" / ("industrial_demo" if args.demo else "ai4i")
```

如果用户给了 --output，就使用它；否则拼接 ROOT/outputs，再按 demo 选择 industrial_demo 或 ai4i。or 在这里返回第一个真值对象，而不是强制返回 True/False。自定义相对路径相对终端当前工作目录解释。

### 第 172 行

```python
    try:
```

开始 try 块，准备捕获下面 analyze 抛出的 ValueError。

### 第 173 行

```python
        analyze(raw, output_dir, demo=args.demo)
```

把原始表、输出目录、演示标记传给 analyze，执行检查、统计、导出和绘图。demo=args.demo 是关键字参数。

### 第 174 行

```python
    except ValueError as error:
```

捕获 try 块执行时的 ValueError，并把异常对象命名为 error。不是捕获所有错误；文件权限、缺少依赖等其他异常仍可能显示完整报错。

### 第 175 行

```python
        parser.exit(1, f"数据格式错误：{error}\n")
```

把捕获的异常转换为简洁的格式错误提示，并用退出码 1 结束程序。第 170 行在 try 外，读 CSV 发生的错误不由这里统一处理。

### 第 178 行

```python
if __name__ == "__main__":
```

直接运行这个文件时，__name__ 等于 "__main__"，条件成立；被其他文件 import 时，__name__ 为模块名，条件不成立，避免导入时自动分析数据。

### 第 179 行

```python
    main()
```

调用 main，启动整个流程。注意：上面函数写在前面，不代表函数体按文件从上到下自动执行；是这里触发 main，再由 main 调用其他函数。

## 用小例子理解三个关键操作

### 布尔标记与筛选

假设 `needs_review` 为 `[False, True, False]`，取反 `~` 后得到 `[True, False, True]`，所以 `clean.loc[...]` 保留第一条和第三条供统计使用。完整记录仍在 `cleaned.csv`。

### 按行和按列

`quality.any(axis=1)` 问“这一行有没有任何一个问题”；`quality.sum()` 默认按列计算，问“这种问题共出现多少次”。编号列必须先排除。

### 故障率

某种类型有 100 条有效记录，其中 8 条故障，故障标签求和为 8，均值为 `8/100=0.08`，图中乘以 100 后显示 8%。这不是模型预测准确率。

## 输出文件

- `cleaned.csv`：所有处理后的记录，包含需要人工复核的记录。
- `quality_flags.csv`：逐行记录问题类型。
- `failure_by_type.csv`：通过检查的记录按 Type 分组后的数量、故障数和故障率。
- `numeric_summary.csv`：完整工作副本的数值概览，仍可能包含已标记的异常范围值。
- `report.txt`：终端报告的文本版本。
- `overview.png`：故障率柱状图和转速/扭矩散点图；没有通过检查的记录时跳过生成。

## 建议练习

1. 运行 `python industrial_analysis.py --demo`，核对总数 13、需复核 7、用于统计 6。
2. 对照第 44～50 行，在质量标记表中找出每个人为问题。
3. 把绘图点大小 `s=18` 改成 `s=40`，重新运行查看区别。
4. 理解检查规则后再尝试更换真实 CSV。不要因为标记异常就直接删除故障样本。

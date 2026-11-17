# 工业故障诊断数据入门

## 运行入门脚本

在项目根目录激活虚拟环境并安装依赖后，先运行教学演示：

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python industrial_analysis.py --demo
```

演示使用人为构造的少量记录，故意加入空值、重复、非法类别和错误数值。输出目录为 `outputs/industrial_demo/`，包含清洗结果、逐行质量标记、统计报告和图表；不代表真实工业数据。

下载官方 AI4I CSV 后，放入 `data/raw/ai4i2020.csv`，再执行：

```bash
python industrial_analysis.py
```

也可以指定其他位置的同结构 CSV：

```bash
python industrial_analysis.py --input /path/to/ai4i2020.csv
```

真实文件的输出默认写入 `outputs/ai4i/`。原始文件不会被覆盖；再次执行会更新对应目录中的分析结果。

## 1. AI4I 2020：先练表格处理和故障分类

- 官方来源：https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset
- 官方下载：https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip
- 性质：模拟工业设备预测性维护场景的合成数据，不是真实设备采集的振动波形。
- 输入包含设备类型、空气温度、工艺温度、转速、扭矩和刀具磨损。
- 标签包含 Machine failure，以及 TWF、HDF、PWF、OSF、RNF 五种故障标记。不同故障标记可以同时出现，不应直接当成互斥的多分类标签。
- UCI 页面标注许可为 CC BY 4.0；使用和分享时保留来源，并在修改后说明改动。

### 清洗与探索任务

1. 用 `head()`、`info()`、`describe()` 检查结构和字段类型。
2. 统计缺失值、完整重复行与 UDI 重复；分别解释它们的意义。
3. 检查 Type 取值、故障标记是否为 0/1，以及温度、转速、扭矩、磨损的范围。
4. 原始温度单位为 K。如需摄氏度，新增列并减去 273.15，不要只修改列名。
5. 按 Type 统计样本量、故障数量和故障率。
6. 比较正常与故障样本的转速、扭矩、磨损分布；将极端值标记为待检查，避免把故障特征当作错误直接删去。
7. 保存清洗记录，保留原始 CSV。

这份数据通常已经比较规整，适合学习数据质量检查，不必为了练习而强行删行或填值。若要练缺失值与重复值修复，应另存教学副本，明确记录人为改动。

### 后续建模注意

- 以 Machine failure 为预测目标时，输入必须排除 Machine failure 与全部五个故障标记，防止标签泄漏。
- UDI 和 Product ID 是标识字段，入门模型先排除，不把它们直接作为故障原因。
- 故障样本较少；做分层划分，报告混淆矩阵、精确率、召回率、F1 和 PR-AUC，并与总预测正常的基线比较。
- 标准化与采样等步骤只在训练集进行；使用验证集调参，测试集留到最终评估。
- 不能根据这份合成数据的成绩宣称模型已适用于真实工厂。

## 2. CWRU：进入轴承振动信号诊断

- 官方入口：https://engineering.case.edu/bearingdatacenter
- 适合：时域波形、RMS、峭度、FFT、包络谱、轴承故障分类。
- 主要以 MATLAB `.mat` 文件发布，可通过 `scipy.io.loadmat` 读取，再按需要转换成 CSV。
- 必须保留每条记录的采样率、测点、工况、原始文件名与标签，避免转换后丢失信号含义。
- 训练/测试应先按原始采集记录或工况划分，再切窗口；不能把同一记录的相邻窗口随机分散到训练和测试集。

## 推荐顺序

先用 AI4I 学习 Pandas、Matplotlib、SQL 和传统机器学习，再用 CWRU 学习 SciPy、信号特征与一维 CNN。AI4I 表格中的一行不是等间隔采样的振动点，不适合直接对其行序列做 FFT。

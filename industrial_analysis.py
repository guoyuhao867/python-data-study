"""AI4I 工业故障数据入门：检查质量、统计故障率、绘图。

真实数据：python industrial_analysis.py
教学演示：python industrial_analysis.py --demo
指定文件：python industrial_analysis.py --input /path/to/ai4i2020.csv
"""

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
FEATURES = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
]
LABELS = ["Machine failure", "TWF", "HDF", "PWF", "OSF", "RNF"]
REQUIRED = ["UDI", "Product ID", "Type", *FEATURES, *LABELS]


def make_demo_data():
    """少量人为构造的教学记录，不代表真实设备或 AI4I 的统计规律。"""
    rows = []
    for i in range(12):
        failed = int(i in (3, 9))
        rows.append({
            "UDI": i + 1,
            "Product ID": f"DEMO{i + 1:03d}",
            "Type": ["L", "M", "H"][i % 3],
            "Air temperature [K]": 298 + i * 0.2,
            "Process temperature [K]": 308 + i * 0.2,
            "Rotational speed [rpm]": 1450 + i * 25,
            "Torque [Nm]": 30 + i * 2,
            "Tool wear [min]": i * 18,
            "Machine failure": failed,
            "TWF": failed,
            "HDF": 0, "PWF": 0, "OSF": 0, "RNF": 0,
        })
    rows[1]["Type"] = " m "
    rows[2]["Torque [Nm]"] = None
    rows[4]["Rotational speed [rpm]"] = "unknown"
    rows[5]["Tool wear [min]"] = -5
    rows[6]["Machine failure"] = 2
    rows[7]["Type"] = "X"
    rows.append(rows[0].copy())
    return pd.DataFrame(rows)


def analyze(raw, output_dir, demo=False):
    missing_columns = sorted(set(REQUIRED) - set(raw.columns))
    if missing_columns:
        raise ValueError(f"CSV 缺少必要字段：{missing_columns}")
    if raw.empty:
        raise ValueError("CSV 没有数据行。")

    output_dir.mkdir(parents=True, exist_ok=True)
    clean = raw.copy()
    # 保留原始文件；只在副本中规范字段，不直接删除可疑记录。
    for column in ["Type", "Product ID"]:
        clean[column] = clean[column].astype("string").str.strip()
        clean[column] = clean[column].replace("", pd.NA)
    clean["Type"] = clean["Type"].str.upper()

    quality = pd.DataFrame(index=raw.index)
    quality["source_record"] = range(1, len(raw) + 1)
    quality["duplicate_full_row"] = raw.duplicated(keep=False)
    quality["missing_product_id"] = clean["Product ID"].isna()
    for column in ["UDI", *FEATURES, *LABELS]:
        clean[column] = pd.to_numeric(clean[column], errors="coerce")
        quality[f"missing_or_non_numeric: {column}"] = clean[column].isna()

    quality["duplicate_udi"] = (
        clean["UDI"].notna() & clean["UDI"].duplicated(keep=False)
    )
    quality["invalid_udi"] = (
        clean["UDI"].isna() | clean["UDI"].le(0) | clean["UDI"].mod(1).ne(0)
    )
    quality["invalid_type"] = ~clean["Type"].isin(["L", "M", "H"])
    for column in LABELS:
        quality[f"invalid_label: {column}"] = ~clean[column].isin([0, 1])
    for column in FEATURES:
        # 这里只检查基础物理范围。数值极端可能与故障有关，不自动删除。
        invalid = clean[column].lt(0)
        if column in FEATURES[:3]:
            invalid = clean[column].le(0)
        quality[f"invalid_range: {column}"] = invalid | clean[column].isin(
            [float("inf"), float("-inf")]
        )

    # 新增摄氏温度列，保留原始 K 单位字段。
    clean["Air temperature [C]"] = clean["Air temperature [K]"] - 273.15
    clean["Process temperature [C]"] = clean["Process temperature [K]"] - 273.15
    clean["needs_review"] = quality.drop(columns="source_record").any(axis=1)

    # 统计仅使用通过上述基础检查的记录；其余记录仍保存在清洗结果中。
    usable = clean.loc[~clean["needs_review"]].copy()
    by_type = usable.groupby("Type")["Machine failure"].agg(
        sample_count="count", failure_count="sum", failure_rate="mean"
    )

    clean.to_csv(output_dir / "cleaned.csv", index=False, encoding="utf-8-sig")
    quality.to_csv(output_dir / "quality_flags.csv", index=False, encoding="utf-8-sig")
    by_type.to_csv(output_dir / "failure_by_type.csv", encoding="utf-8-sig")
    clean[FEATURES].describe().to_csv(output_dir / "numeric_summary.csv")

    report = [
        "【教学合成演示数据】" if demo else "AI4I 数据检查报告",
        f"输入记录数：{len(raw)}",
        f"需人工检查的记录数：{int(clean['needs_review'].sum())}",
        f"用于故障率统计的记录数：{len(usable)}",
        "同一记录可能触发多种质量标记，标记次数不能直接相加作为行数。",
        "重复标记覆盖重复组内全部记录；统计暂时排除整组，待核实后再决定保留哪条。",
        "未填补缺失值、未删除原始记录、未自动删除极端值。",
        "清洗统计可能改变样本分布，分析时应核实被排除的记录。",
        "演示数据不用于推断真实设备故障规律。" if demo else "",
        "\n各项质量标记数量：",
        quality.drop(columns="source_record").sum().to_string(),
        "\n原始数据缺失值：",
        raw.isna().sum().to_string(),
        "\n按设备类型统计：",
        by_type.to_string(),
    ]
    report_text = "\n".join(report)
    (output_dir / "report.txt").write_text(report_text, encoding="utf-8")
    print(report_text)

    if not usable.empty:
        import matplotlib

        # 使用非交互式绘图，图片保存到文件，无需弹出窗口。
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(11, 4))
        (by_type["failure_rate"] * 100).plot.bar(ax=axes[0], rot=0)
        axes[0].set(title="Failure rate by type", xlabel="Type", ylabel="Failure rate (%)")
        for label, group in usable.groupby("Machine failure"):
            axes[1].scatter(
                group["Rotational speed [rpm]"], group["Torque [Nm]"],
                label="Failure" if label == 1 else "Normal", alpha=0.6, s=18,
            )
        axes[1].set(xlabel="Speed (rpm)", ylabel="Torque (Nm)")
        axes[1].legend()
        if demo:
            fig.suptitle("SYNTHETIC TEACHING DEMO")
        fig.tight_layout()
        fig.savefig(output_dir / "overview.png", dpi=150)
        plt.close(fig)
    else:
        print("没有通过基础检查的记录，跳过绘图。")
    print(f"\n结果已保存到：{output_dir}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/raw/ai4i2020.csv")
    parser.add_argument("--output", type=Path, help="自定义输出目录")
    parser.add_argument("--demo", action="store_true", help="使用人为构造的教学记录")
    args = parser.parse_args()
    if args.demo:
        raw = make_demo_data()
    else:
        if not args.input.is_file():
            parser.exit(1, f"未找到 CSV：{args.input}\n请下载 AI4I 数据，或先运行：python industrial_analysis.py --demo\n")
        raw = pd.read_csv(args.input)
    output_dir = args.output or ROOT / "outputs" / ("industrial_demo" if args.demo else "ai4i")
    try:
        analyze(raw, output_dir, demo=args.demo)
    except ValueError as error:
        parser.exit(1, f"数据格式错误：{error}\n")


if __name__ == "__main__":
    main()

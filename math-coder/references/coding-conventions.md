# 编码规范

面向数学建模竞赛的代码约定。目标是让结果**跑得通、看得懂、可复现、能直接进论文**。

## 目录

```
solving/
├── code/          q1_<name>.py, q2_<name>.py, ...   （逐问一个脚本）
├── data/
│   ├── raw/       题目附件原样副本，只读不改
│   └── processed/ 预处理后数据 + 字段说明
├── results/       结果表 (csv/xlsx) + run-log.md
└── figures/       图 (png 300dpi + pdf/svg 矢量)
```

`solving/` 而非 `code/`：项目根的 `code/` 是组合模型案例库，不要覆盖。

## 命名

| 对象 | 约定 | 例 |
| --- | --- | --- |
| 脚本 | `q<小问号>_<英文短名>.py` | `q1_siting_mclp.py` |
| 图 | `问题<N>-<类别>-图<N>-<序>.png` | `问题2-预测-图2-1.png` |
| 表 | `问题<N>-表<N>-<名称>.csv` | `问题2-表2-1-SINR参数.csv` |
| 中间结果 | `q<N>_<名称>.csv` | `q3_weights.csv` |

**编号按小问，不按论文章节**——这是与写作手的交接约定：

- 图号 / 表号里的第一个数字是**小问号**，不是论文里的章节号。你不可能知道论文会把问题 2 排在第几章，所以不要按章节猜。论文图号就取 `图<N>-<序>`，与文件名里的编号完全一致。
- 写作手用**显式编号**形式原样引用（`![图2-1：题注](...)`、`表2-1：题注`），不重新编号。
- 因此：同一个 `<N>` 在小问号、文件名、论文编号三处必须相同；`<序>` 在该小问内从 1 连续。

## 单脚本骨架

```python
# -*- coding: utf-8 -*-
"""问题1：<模型名> —— <一句话目标>。契约条目：§<章节>。"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")                      # 无界面环境必须；否则 savefig 可能挂起
import matplotlib.pyplot as plt

SEED = 42
ROOT = Path(__file__).resolve().parents[1]  # -> solving/
DATA, OUT, FIG = ROOT / "data", ROOT / "results", ROOT / "figures"


def setup_style():
    plt.rcParams.update({
        # 拉丁字符走 serif(Times New Roman)，中文走 sans-serif(SimSun) 逐字回退
        "font.family": ["serif", "sans-serif"],
        "font.serif": ["Times New Roman"],
        "font.sans-serif": ["SimSun"],
        "axes.unicode_minus": False,                   # 负号正常显示
        "font.size": 14, "axes.labelsize": 14,
        "xtick.labelsize": 12, "ytick.labelsize": 12, "legend.fontsize": 12,
        "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
    })


def load_data():
    """读取预处理数据。返回字段与单位见 data/processed/README。"""
    ...


def build_model(df, **params):
    """按契约 §<章节> 构造目标函数、约束与参数。"""
    ...


def solve(model, **params):
    """求解并返回结果对象。"""
    ...


def save_results(result):
    (OUT / "q1_solution.csv").write_text("", encoding="utf-8")  # 替换为真实写盘
    return OUT / "q1_solution.csv"


def make_figures(result):
    fig, ax = plt.subplots(figsize=(6, 4))
    ...
    fig.savefig(FIG / "问题1-结果图像-图1-1.png")
    fig.savefig(FIG / "问题1-结果图像-图1-1.pdf")   # 与文件名编号一致，写作手直接引用
    plt.close(fig)


def main():
    setup_style()
    np.random.seed(SEED)
    df = load_data()
    model = build_model(df)
    result = solve(model)
    path = save_results(result)
    make_figures(result)
    print(f"[q1] 目标值={result['obj']:.4f} 约束满足={result['feasible']} -> {path}")


if __name__ == "__main__":
    main()
```

要点：

- 路径全部由 `Path(__file__)` 推导，**不写绝对路径**。
- 参数集中在配置区或函数签名，函数体内**不出现魔法数字**。
- 关键中间量（目标值、系数、权重、误差）用 `print` 输出——`run_all.py` 会收集。
- 结构按「读数据 → 建模 → 求解 → 落盘 → 出图」分函数，便于单独调试。

## 绘图

- 必须：标题、坐标轴标签（含单位）、图例。缺一不可。
- **中文字体**：`font.family` 必须是**列表** `["serif", "sans-serif"]`，拉丁字符取 `font.serif`（Times New Roman），中文逐字回退到 `font.sans-serif`（SimSun）。写成单个 `"font.family": "serif"` 并指望 `font.serif` 列表内部回退是**不生效**的——只会得到方框和 `Glyph ... missing from font(s)` 警告。
- 自检：运行后 stderr 若出现 `missing from font`，说明字体没配对，图不能进论文。
- 双导出：`png`（300 dpi，给 Word）+ `pdf`/`svg`（矢量，给 LaTeX）。
- 图下结论写在脚本注释或报告里（如「图 3 显示方案 2 成本比方案 1 低 15%」），不要画在图上遮挡数据。
- 配色克制，同一论文内同义曲线用同一颜色；对比色系用 `tab10` 或 `viridis`。

## 结果落盘

- 表格优先 `csv`（`encoding="utf-8-sig"`，Excel 中文不乱码）；多表合并或需格式时用 `xlsx`。
- 每个结果表必须有可辨识的列名与单位；浮点保留位数一致（一般 4 位）。
- 同时写一份机器可读的结果，避免只在 stdout 里出现数字。

## 复现

- 固定 `np.random.seed(SEED)`；元启发式、bootstrap、扰动都设种子。
- 记录环境：Python 版本与关键库版本写入 `run-log.md`。
- 随机算法多次独立运行时，报告**最优值、均值、标准差**，不只报最优。
- 迭代类算法保存收敛曲线数据，便于复现与画图。

## 健壮性

- `matplotlib.use("Agg")` + `plt.close(fig)`：避免内存泄漏与挂起。
- `warnings.filterwarnings("ignore")`：屏蔽第三方库噪声，但不要掩盖自己的错误。
- 数值保护：除零、`log(0)`、指数溢出用 `max(x, eps)` / `np.clip` 处理。
- 求解器给失败分支：不可行、不收敛、超时都要有明确输出，而不是静默返回空。

## Python 还是 Matlab

- 默认 Python：模板、组合模型案例与大多数 `write/` 代码包都是 Python。
- 题目或团队指定 Matlab 时用 `.m`，保持同样的「配置区 → 读数据 → 建模 → 求解 → 落盘 → 出图」结构；`run_all.py` 只自动跑 `.py`，`.m` 需在 MATLAB 中手动执行并把输出补进 `run-log.md`。

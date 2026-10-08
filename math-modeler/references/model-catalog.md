# 模型库目录（54 类）

项目根 `resource/` 下的模型检索目录。每个目录同时提供 Matlab（`.m`）与 Python（`.py`）实现；下表只列 Python 路径，同目录 `.m` 为等价 Matlab 版。

**用法**：先按题型定位分组，再按「适用信号」和「数据门槛」筛候选，最后用「输出」「检验」设计契约与验收。目录外的模型按「自建模型」处理。

**另有组合模型实现**：`code/2025研赛创新型算法+源代码汇总！/` 下有 45 个**组合模型**案例（题目+源码），覆盖随机森林、XGBoost、SVM、ARIMA、LSTM、CNN、Attention、小波、因子分析等的两两组合。单模型不够用时去那里找组合结构，索引见 `math-coder/references/example-library.md`。

- [A. 优化类（12）](#a-优化类12)
- [B. 预测类（10）](#b-预测类10)
- [C. 评价类（8）](#c-评价类8)
- [D. 分类与聚类（8）](#d-分类与聚类8)
- [E. 降维与可视化（3）](#e-降维与可视化3)
- [F. 统计检验与数据预处理（6）](#f-统计检验与数据预处理6)
- [G. 机理/微分方程模型（3）](#g-机理微分方程模型3)
- [H. 数值方法（1）](#h-数值方法1)
- [I. 机器学习（分类与回归通用）（3）](#i-机器学习分类与回归通用3)

---

## A. 优化类（12）

| 模型 | 适用信号 | 数据门槛 | 输出 | 代码 |
| --- | --- | --- | --- | --- |
| 线性规划 | 目标与约束均线性、决策变量连续 | 只需系数矩阵与右端项 | 最优解、影子价格、约束使用率 | `resource/线性规划模型Matlab+Python代码/linear_programming.py` |
| 整数规划 | 决策变量必须取整（人数、台数、批次） | 系数矩阵；规模受求解器限制 | 整数最优解 | `resource/整数规划模型/integer_programming.py` |
| 0-1 规划 | 是/否选择、选址、指派、背包 | 0-1 决策变量 | 选中方案 | `resource/0-1规划模型Matlab+Python代码/zero_one_programming.py` |
| 非线性规划 | 目标或约束含非线性（成本曲线、距离、乘积项） | 可解析的连续模型、初值 | 局部/全局最优解 | `resource/非线性规划模型Matlab+Python代码/nonlinear_programming.py` |
| 多目标规划 | 多个相互冲突的目标需权衡 | 各目标可量化 | Pareto 解集、权重敏感性 | `resource/多目标规划模型Matlab+Python代码/multi_objective_programming.py` |
| 动态优化（动态规划） | 多阶段序贯决策、状态可离散 | 状态空间规模可控 | 阶段最优策略与最优值 | `resource/动态优化模型Matlab+Python代码/dynamic_programming.py` |
| 遗传算法 | NP 难、非凸、多峰、组合优化 | 只需可计算适应度函数 | 近似最优解、收敛曲线 | `resource/遗传算法Matlab+Python代码/genetic_algorithm.py` |
| 粒子群算法 | 连续或组合黑箱优化、约束不可解析 | 适应度函数 | 近似最优解、收敛曲线 | `resource/粒子群算法Matlab+Python代码/particle_swarm.py` |
| 模拟退火 | 组合爆炸、可行解可做邻域变换 | 邻域算子、降温策略 | 近似最优解 | `resource/模拟退火Matlab+Python代码/simulated_annealing.py` |
| 最速下降法 | 无约束或凸可微优化，需展示梯度法推导 | 梯度可求 | 迭代序列与最优解 | `resource/最速下降法/steepest_descent.py` |
| Dijkstra（单源最短路） | 单源到各点最短路径、边权非负 | 邻接矩阵或边表 | 最短路长与路径 | `resource/Dijkstra 算法（最短路径算法）Matlab+Python代码/dijkstra_algorithm.py` |
| Floyd（全源最短路） | 任意两点间最短路径、图规模小 | 邻接矩阵 | 全源距离矩阵与路径 | `resource/Floyd 算法（全源最短路径算法）Matlab+Python代码/floyd_algorithm.py` |

---

## B. 预测类（10）

| 模型 | 适用信号 | 数据门槛 | 输出 | 代码 |
| --- | --- | --- | --- | --- |
| 回归分析 | 影响因素 → 连续目标、关系近似线性 | 样本数远大于自变量数，检查共线性与显著性 | 回归方程、系数、R²、残差 | `resource/回归分析预测模型Matlab+Python代码/regression_analysis.py` |
| 灰色预测 GM(1,1) | 小样本、近似指数增长、信息不完全 | 4–10 个等间隔点 | 短期预测、后验差比 C、小误差概率 P | `resource/灰色预测模型Matlab+Python代码/grey_prediction.py` |
| ARMA 时间序列 | 平稳序列、自相关/偏自相关结构明显 | 一般 ≥50 点，需差分平稳化并定阶 | 时序预测、AIC/BIC 定阶结果 | `resource/ARMA时间序列预测模型Matlab+Python代码/arma_prediction.py` |
| ARIMA / SARIMA | 非平稳序列、含趋势，季节版再含周期波动 | ≥50 点；季节项建议 ≥4 个完整周期（如月度 ≥48 点） | 时序预测、95% 区间、AIC/BIC 定阶 | `resource/ARIMA-SARIMA时间序列预测模型Matlab+Python代码/arima_sarima.py` |
| 二次指数平滑 | 存在线性趋势的序列、短期预测 | ≥10 点 | 平滑预测值、平滑系数 | `resource/二次指数平滑预测Matlab+Python代码/quadratic_exponential_smoothing.py` |
| 季节指数 | 明显周期性（季节性、月度节律） | ≥2 个完整周期 | 季节指数、趋势外推预测 | `resource/季节指数预测模型Matlab+Python代码/seasonal_index_prediction.py` |
| 马尔可夫预测 | 状态转移、满足无后效性、状态可离散 | 状态序列或转移频数矩阵 | 状态概率、稳态分布 | `resource/马尔可夫预测模型Matlab+Python代码/markov_prediction.py` |
| Logistic 预测 | 因变量为二分类或概率、S 型增长过程 | 中等样本，需避免完全分离 | 概率预测、分类阈值、AUC | `resource/Logistic预测模型Matlab+Python代码/logistic_prediction.py` |
| BP 神经网络预测 | 高维非线性、机理不清、样本较多 | 通常 ≥数百样本，需归一化 | 非线性预测、拟合误差 | `resource/BP神经网络预测模型Matlab+Python代码/bp_neural_network.py` |
| 高斯过程回归 | 小样本、需要预测的不确定性区间 | 数十至数百样本 | 预测均值与置信区间 | `resource/高斯回归预测模型Matlab+Python代码/gaussian_process_regression.py` |

回归类任务若线性关系不成立或需特征重要性，改用监督学习模型（SVR、随机森林、XGBoost），见 [I 类](#i-机器学习分类与回归通用3)。

中长期总量趋势预测优先用机理模型（人口模型、传染病模型），见 [G 类](#g-机理微分方程模型3)。

---

## C. 评价类（8）

| 模型 | 适用信号 | 数据门槛 | 输出 | 代码 |
| --- | --- | --- | --- | --- |
| 层次分析法（AHP） | 指标呈层次结构、需主观权重、可专家判断 | 判断矩阵；指标数不宜过多 | 权重、一致性比率 CR | `resource/层次分析法Matlab+Python代码/ahp_python_final.py` |
| 熵权法 | 需客观权重、指标数据完整 | 数据矩阵；指标变异需非零 | 客观权重、综合得分 | `resource/熵权法Matlab+Python代码/entropy_python_final.py` |
| TOPSIS | 多方案逼近理想解排序 | 数据矩阵，需先正向化 | 相对贴近度、排序 | `resource/TOPSIS综合评价法Matlab+Python代码/topsis_python_final.py` |
| 模糊综合评价 | 指标边界模糊、需隶属度描述等级 | 隶属函数或专家评分 | 隶属度向量、评价等级 | `resource/模糊综合评价法Matlab+Python代码/fuzzy_python_final.py` |
| 灰色关联分析 | 小样本、找主要影响因素、数据量少 | 少量参考/比较序列 | 关联度排序 | `resource/灰色关联分析法Matlab+Python代码/grey_python_final.py` |
| 秩和比（RSR） | 高优/低优指标混合、需综合评价与分档 | 数据矩阵 | RSR 值、分档与排序 | `resource/秩和比综合评价法/rsr_python_final.py` |
| DEA | 多投入多产出的效率评价 | DMU 数量 ≥ 2×(投入数+产出数) | 效率值、松弛变量、规模报酬 | `resource/DEA综合评价法Matlab+Python代码/dea_python_final.py` |
| 神经网络综合评价 | 非线性、大样本、有评价标签 | 样本较多且有监督信号 | 综合评分 | `resource/神经网络综合评价法Matlab+Python代码/nn_python_final.py` |

指标相关性高、需先压缩时，先做 PCA 降维（见 [E 类](#e-降维与可视化3)）再评价。

---

## D. 分类与聚类（8）

| 模型 | 适用信号 | 数据门槛 | 输出 | 代码 |
| --- | --- | --- | --- | --- |
| KNN 分类 | 小样本、低维、决策边界不规则 | 有标签样本，需定 k 与距离 | 类别标签、准确率 | `resource/KNN 分类模型Matlab+Python代码/knn_classification.py` |
| 决策树 | 需要可解释的分类规则、特征混合 | 有标签样本 | 分类规则树、特征重要性 | `resource/决策树分类模型Matlab+Python代码/decision_tree_classification.py` |
| 朴素贝叶斯 | 分类、特征条件独立假设可接受 | 有标签样本 | 后验概率、类别 | `resource/朴素贝叶斯分类模型Matlab+Python代码/naive_bayes_classification.py` |
| BP 神经网络分类 | 非线性边界、样本较多 | ≥数百有标签样本 | 类别概率、混淆矩阵 | `resource/BP 神经网络分类模型Matlab+Python代码/bp_neural_network.py` |
| K-means | 球形簇、需先定 k、样本量大 | 数值特征，需标准化 | 硬聚类、轮廓系数 | `resource/K-means 聚类算法Matlab+Python代码/kmeans_clustering.py` |
| 层次聚类 | 不需预设 k、需要谱系结构 | 距离矩阵 | 层次树（树状图） | `resource/层次聚类算法Matlab+Python代码/hierarchical_clustering.py` |
| 高斯混合（GMM） | 簇有重叠、需软聚类概率 | 数值特征 | 隶属概率、EM 收敛 | `resource/高斯混合聚类模型（GMM）/gaussian_mixture.py` |
| SOM 自组织神经网络 | 高维聚类 + 拓扑可视化 | 数值特征 | 拓扑映射、簇归属 | `resource/SOM 自组织神经网络Matlab+Python代码/som_clustering.py` |

分类任务若样本少而维度高、或非线性边界明显，改用 SVM / 随机森林 / XGBoost，见 [I 类](#i-机器学习分类与回归通用3)。

---

## E. 降维与可视化（3）

| 模型 | 适用信号 | 数据门槛 | 输出 | 代码 |
| --- | --- | --- | --- | --- |
| PCA 主成分分析 | 线性降维、指标共线、需客观权重 | 数据矩阵，建议标准化 | 主成分得分、方差贡献率 | `resource/PCA 主成分分析法Matlab+Python代码/pca_analysis.py` |
| t-SNE | 高维聚类结果的二维可视化、重局部结构 | 中小规模 | 2/3 维嵌入 | `resource/T-SNE 降维算法Matlab+Python代码/t_sne_analysis.py` |
| UMAP | 高维可视化、需保留更多全局结构且更快 | 中小规模 | 低维嵌入 | `resource/UMAP 降维法Matlab+Python代码/umap_analysis.py` |

---

## F. 统计检验与数据预处理（6）

| 模型 | 适用信号 | 数据门槛 | 输出 | 代码 |
| --- | --- | --- | --- | --- |
| 连续变量相关性 | 连续-连续关联，需方向与强度 | 一般 ≥30 样本 | 协方差、Pearson/Spearman 系数与 p 值 | `resource/连续变量相关性分析：协方差、Pearson、SpearmanMatlab+Python代码/continuous_correlation_analysis.py` |
| Kendall 相关系数 | 等级数据、小样本、存在大量并列 | 等级或连续数据 | Kendall τ 与显著性 | `resource/Kendall 相关系数（特殊的相关性分析）Matlab+Python代码/kendall_correlation.py` |
| 卡方检验 | 离散-离散变量的独立性 | 列联表期望频数 ≥5 | χ² 统计量、p 值 | `resource/离散变量相关性分析：卡方检验Matlab+Python代码/chi_square_test.py` |
| 离散-连续相关性（箱型图） | 分组间连续变量的差异可视化与检验 | 分组连续数据 | 箱型图、组间差异结论 | `resource/离散变量和连续变量的相关性分析：箱型图Matlab+Python代码/boxplot_discrete_continuous.py` |
| 箱型图异常值检测 | 异常值识别，IQR 法，分布未知时稳妥 | 数值序列 | 异常点清单 | `resource/箱型图检测异常值Matlab+Python代码/boxplot_outlier_detection.py` |
| 标准差法异常值检测 | 近似正态数据的异常检测（3σ） | 数值序列，近似正态 | 异常点清单 | `resource/标准差法检测异常值Matlab+Python代码/std_outlier_detection.py` |

---

## G. 机理/微分方程模型（3）

| 模型 | 适用信号 | 数据门槛 | 输出 | 代码 |
| --- | --- | --- | --- | --- |
| 人口模型 | 种群/人口总量演化、Logistic 或 Malthus 生长 | 历史总量序列 | 中长期趋势、承载力参数 | `resource/人口模型Matlab+Python代码/population_model.py` |
| 传染病模型 | 传播机理建模（SIR/SEIR 类） | 感染/康复/移除序列 | 峰值、峰值时间、传播规模 | `resource/传染病模型Matlab+Python代码/epidemic_model.py` |
| 战争模型 | 双方对抗消耗的作战/竞争机理 | 兵力或资源存量序列 | 对抗进程与胜负条件 | `resource/战争模型Matlab+Python代码/war_model.py` |

---

## H. 数值方法（1）

| 模型 | 适用信号 | 数据门槛 | 输出 | 代码 |
| --- | --- | --- | --- | --- |
| 拉格朗日插值 | 已知离散点需补全中间值或构造解析式 | 节点数适中，注意龙格现象 | 插值多项式与插值值 | `resource/拉格朗日插值法Matlab+Python代码/lagrange_interpolation.py` |

---

## I. 机器学习（分类与回归通用）（3）

同一套算法既能做回归也能做分类（换损失函数即可），因此单列一类。**共同前提：特征必须标准化、必须用交叉验证调参、必须留出独立测试集。** 每个脚本都同时给出回归与分类两个案例。

| 模型 | 适用信号 | 数据门槛 | 输出 | 代码 |
| --- | --- | --- | --- | --- |
| 支持向量机 SVM/SVR | 小样本 + 高维 + 非线性；对离群点稳健 | 数十至数百样本；需调 C 与 gamma | 分类标签 / 回归值、支持向量、准确率 / R² | `resource/SVM-SVR模型Matlab+Python代码/svm_svr.py` |
| 随机森林 | 表格数据、非线性、需特征重要性；对调参不敏感、不易过拟合 | 数百样本以上 | 预测值 / 类别、OOB 泛化误差、特征重要性 | `resource/随机森林模型Matlab+Python代码/random_forest.py` |
| XGBoost / 梯度提升树 | 表格数据精度优先；需早停、特征重要性与可解释性 | 数百样本以上，特征数适中 | 预测值 / 概率、特征重要性、学习曲线 | `resource/XGBoost模型Matlab+Python代码/xgboost_model.py` |

**三者的取舍**：样本少（<200）优先 SVM/SVR；样本中等、要稳、要特征重要性选随机森林；追求表格数据最高精度且愿调参选 XGBoost。数据量大且为图像/序列时，改用 `code/` 下的 CNN-LSTM / GRU-Attention 等组合案例。

**检验配套**：分类报准确率/精确率/召回率/F1/AUC + 混淆矩阵；回归报 RMSE/MAE/R²；三者都要做 k 折交叉验证，并至少用一条独立路径复核（换模型族或留出集）。判分标准见 `math-coder/references/verification-metrics.md`。

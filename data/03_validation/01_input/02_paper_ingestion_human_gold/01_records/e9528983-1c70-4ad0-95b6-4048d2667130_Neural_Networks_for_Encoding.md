Neural Networks for Encoding
hasModelName
NN-Encoded Dynamic Security-Constrained AC-OPF
神经网络编码动态安全约束 AC-OPF 模型
hasPaperTitle
Neural Networks for Encoding Dynamic Security-Constrained Optimal Power
Flow
hasPublicationYear
2022
hasDOI
上传 PDF 中未明确标注 DOI
补充标识：arXiv:2003.07939v5
hasAuthor
Ilgiz Murzakhanov; Andreas Venzke; George S. Misyris; Spyros
Chatzivasileiadis
hasInstitution
Department of Wind and Energy Systems, Technical University of Denmark
2. MotivationAndSolvedProblem
模型提出动机与解决的问题
hasPrimaryPurpose
该模型主要用于把原本难以直接加入 OPF 的动态安全约束，例如小信号稳定约束，用
神经网络编码成可嵌入优化模型的线性混合整数约束，从而把动态安全约束 AC-OPF
近似转化为 MILP 求解。
hasMotivation
AC-OPF 可以处理静态运行约束，例如电压约束和线路潮流约束；但如果直接加入动
态安全约束，例如小信号稳定或暂态稳定约束，问题会变得非常复杂甚至不可处理。
传统方法通常需要迭代求解 NLP，或者针对某一种稳定性指标做特殊近似，通用性和
可扩展性有限。因此论文提出用分类神经网络学习“可行域”，再把训练好的 ReLU 神
Neural Networks for Encoding
1

经网络精确转化为 mixed-integer linear constraints，使动态安全约束能够进入优化
问题。
hasSolvedProblem
解决了动态安全约束难以直接加入 AC-OPF 的问题。该方法把满足静态安全约束和动
态安全约束的控制变量区域学习为神经网络分类边界，然后通过 ReLU 神经网络的精
确 MILP 重构，把这个边界作为优化约束加入 OPF。论文重点展示了 N-1 security 和
small-signal stability 同时存在时的动态安全约束 AC-OPF。
hasResearchQuestion
是否可以用分类神经网络编码 AC-OPF 的静态与动态安全可行域，并通过神经网络的
精确混合整数线性重构，把原本难处理的动态安全约束 AC-OPF 转化为可求解的
MILP，同时获得成本较优且满足安全约束的调度方案？
hasPrimaryOutput
模型主要输出：
发电机有功出力设定 pg
发电机电压设定 vg
满足 N-1 security 和 small-signal stability 的可行调度
运行成本
可行性分类结果
AC power flow 恢复后的系统状态
不同保守性参数 ε 下的可行率和成本变化
3. ModelFeature
模型特征标签
hasModelFeature
DynamicSecurityConstrainedOPF; NeuralNetworkEncodedFeasibleSpace;
MILPEncodedOPF; SmallSignalStabilityConstrainedOPF
hasPowerFlowFormulationFeature
ACOPF; SecurityConstrainedACOPF
hasTimeHorizonFeature
StaticOPF; SinglePeriodOPF; DynamicSecurityConstrainedOPF
Neural Networks for Encoding
2

hasTemporalResolution
不适用。模型不是多时间步调度，而是单运行点下的动态安全约束调度。
hasOptimizationHorizon
Single operating condition
hasUncertaintyHandlingFeature
DeterministicOPF; SecurityConstrainedOPF
说明：它考虑 N-1 contingency 和小信号稳定，但不是随机优化或概率约束优化。
hasPowerSystemDomainFeature
TransmissionNetworkOPF; DynamicSecurityAssessmentOPF
hasSolutionMethodEnhancementFeature
LearningAssistedOPF; NeuralNetworkEncoding; MixedIntegerReformulation;
MILPApproximation; IterativeLinearization; ReLUReformulation
hasModelPerformanceFeature
ScalableForLargeSystem; FeasibilityOriented; DynamicSecuritySuitable;
CostOptimalApproximation
hasDemandSideFeature
FixedLoad
4. ModelStructure
模型结构信息
hasObjectiveFunction
目标函数是最小化系统发电成本。
minimize f(pg0)
其中 pg0 表示 intact system state，也就是正常运行状态下的发电机有功出力。
hasConstraintFunction
主要约束包括：
发电机有功出力上下限约束
发电机无功出力上下限约束
母线电压上下限约束
Neural Networks for Encoding
3

线路视在功率约束
AC power flow balance 约束
N-1 contingency 下的运行约束
preventive control 约束，即事故发生后发电机有功设定和电压设定保持固定
small-signal stability 约束
系统矩阵 A 的特征值约束
最小阻尼比 γmin 约束
神经网络可行域分类约束 z1 ≥ z2
加入保守性后的分类约束 z1 ≥ z2 + ε
ReLU 神经元的 mixed-integer linear reformulation 约束
主动功率损耗 plosses 的一阶 Taylor 线性化约束
usesParameter
pg; vg; p; q; v; θ; pmin; pmax; qmin; qmax; vmin; vmax; sline; smaxline;
sbalance; C; A; λ; ν; γmin; W; b; y; yhat; z; ε; ρ; plosses; δplosses/δpg;
δplosses/δvg; ReLU binary variables; contingency set; generator set G; bus set
N; line set L.
hasSolutionDetailsSummary
该方法首先采样控制变量 u = [pg0, vg0]，判断对应运行点是否满足 AC-OPF 静态约
束、N-1 安全约束和 small-signal stability 约束，然后训练一个二分类神经网络来表
示可行 / 不可行区域。训练好的 ReLU 神经网络被精确转化为 MILP 约束：每个
ReLU 神经元引入一个二进制变量，从而把神经网络分类边界嵌入优化模型。为了处
理 AC power flow 的非线性等式，论文把系统有功功率平衡中的 loss term 用一阶
Taylor 展开进行迭代线性化，所以最终通过不断求解 MILP 来近似原来的动态安全约
束 AC-OPF。
hasModelValidationSummary
论文使用 IEEE 14-bus 系统验证方法。系统包含 5 台发电机、11 个负荷和 20 条线
路。N-1 security 中考虑线路故障，但排除了会导致问题不可行的线路 7-8 和 6-13。
小信号稳定模型使用 tenth-order synchronous machine model，最低阻尼比要求为
γmin = 3%。数据集包含 45000 个样本，50% 可行、50% 不可行，80% 用于训
练，20% 用于测试。神经网络有 3 个隐藏层，每层 50 个神经元，使用 TensorFlow
训练，并将权重稀疏性逐步提高到 50%。MILP 用 YALMIP 建模、Gurobi 求解。实
验使用 125 个随机线性成本函数测试。
Neural Networks for Encoding
4

hasFindingsSummary
训练后的神经网络在测试集上的预测准确率为 99%。传统 AC-OPF 和 N-1 security
constrained AC-OPF 在 125 个随机测试实例中只有 35.2% 返回满足全部安全要求
的可行解；加入小信号稳定的 NN-MILP 方法在 ε = 0 时可行率为 52.8%，ε = 7 时
为 84.0%，ε = 8 时达到 100.0%。N-1 security 使平均成本增加 5.7%，加入
small-signal stability 又额外增加 15.6%；但把 ε 从 7 增加到 8 使可行率从 84.0%
到 100.0% 时，额外成本只增加 0.033%。主动功率损耗的迭代线性化平均 7 次迭代
收敛。
hasStrengthsAndLimitationsSummary
优点：该模型能把原本难以显式处理的动态安全约束编码进优化问题，尤其适合
small-signal stability 这类基于微分方程 / 特征值的约束。相比直接把动态约束放入
AC-OPF，它更可求解；相比单纯安全评估神经网络，它还能输出成本优化后的调度
方案。
限制：该方法存在近似误差，不能保证无最优性损失；神经网络可行域边界可能误
判，因此需要 ε 增加保守性；不同电网通常需要重新训练神经网络；实验主要在 IEEE
14-bus 系统上验证，尚未证明在大规模真实系统中同样有效。
isScenarioSuitability
适合场景：
动态安全约束 AC-OPF
N-1 security + small-signal stability 联合约束
需要把难处理稳定性约束转化为 MILP 的场景
需要在安全性和成本之间调节保守性的场景
不适合场景：
不需要动态安全约束的普通 AC-OPF
大规模系统且没有足够可行 / 不可行样本训练神经网络
需要严格全局最优和严格稳定性证明的场景
随机风电 / 光伏概率建模场景
hasFurtherProperty
该论文的核心不是“预测 OPF 最优解”，而是“学习安全可行域”。也就是说，它不直接
让神经网络输出 pg、vg，而是让神经网络判断某组 pg、vg 是否在满足 N-1 和小信
号稳定的安全可行域内，再把这个判断变成 MILP 约束。
Neural Networks for Encoding
5

objective property 对象属性
hasObjectiveFunction
GenerationCostMinimization; SecurityFeasibleDispatchOptimization
hasConstraintFunction
ACPowerBalanceConstraint; VoltageLimitConstraint;
GeneratorActivePowerLimitConstraint; GeneratorReactivePowerLimitConstraint;
LineFlowLimitConstraint; NMinusOneSecurityConstraint;
SmallSignalStabilityConstraint; DampingRatioConstraint;
NeuralNetworkFeasibilityConstraint; ReLUEncodingConstraint;
IterativeLossLinearizationConstraint
usesParameter
Pg; Qg; Vm; Va; p; q; v; θ; pmin; pmax; qmin; qmax; vmin; vmax; sline;
smaxline; A; λ; ν; γmin; W; b; z; ε; plosses; contingency set
hasMathematicalProblemType
NLP; MINLP; MILP; MixedIntegerLinearApproximation;
DynamicSecurityConstrainedOptimization
hasModeledEnergySector
Electricity
Neural Networks for Encoding
6

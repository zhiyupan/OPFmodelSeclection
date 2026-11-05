Optimal Power Flow Using
Graph Neural Networks
1. PaperMetadata
hasModelName
GNN-based OPF Imitation Learning Model
基于图神经网络的 OPF 模仿学习模型
hasPaperTitle
Optimal Power Flow Using Graph Neural Networks
hasPublicationYear
2020
hasDOI
论文 PDF 中未明确给出 DOI
hasAuthor
Damian Owerko; Fernando Gama; Alejandro Ribeiro
hasInstitution
Department of Electrical and Systems Engineering, University of Pennsylvania
2. MotivationAndSolvedProblem
hasPrimaryPurpose
使用 Graph Neural Networks 学习并近似 ACOPF 的最优解，使 OPF 求解在测试阶
段更加快速、局部化和可扩展。
hasMotivation
ACOPF 因为交流潮流方程中的非线性和三角函数关系而非凸、难求解。DCOPF 虽然
快，但在重载电网中小角度近似不再可靠。已有机器学习方法如 MLP 不利用电网拓扑
结构，容易过拟合，且扩展到大规模电网时效果差。因此需要一种利用电网图结构的
学习模型。
hasSolvedProblem
Optimal Power Flow Using Graph Neural Networks
1

解决传统 ACOPF 求解计算慢、现有神经网络方法不局部、不易扩展的问题。GNN 使
用电网拓扑作为图结构，通过邻居信息交换预测发电机最优有功出力，从而近似
IPOPT 求得的 ACOPF 解。
hasResearchQuestion
GNN 是否能够通过模仿学习近似 IPOPT 的 ACOPF 最优解，并在 IEEE-30 和 IEEE-
118 系统上比 MLP 更准确、更快、更可扩展？
hasPrimaryOutput
预测的发电机节点有功出力 p* 的近似值。论文主要输出不是完整 OPF 解，而是
generator active power output 的预测结果，以及相对 RMSE 和计算时间对比。
3. ModelFeature
hasModelFeature
DataDrivenOPF; LearningAssistedOPF; GraphNeuralNetwork; ImitationLearning;
ScalableOPFApproximation; LocalInformationProcessing
hasPowerFlowFormulationFeature
ACOPF
说明：目标解来自 IPOPT 求解的 ACOPF。DCOPF 只用于生成 sub-optimal state /
warm start，不是最终目标模型。
hasTimeHorizonFeature
StaticOPF; SinglePeriodOPF
hasTemporalResolution
论文未给出固定时间分辨率。模型针对单个电网状态快照进行 OPF 预测。
hasOptimizationHorizon
单个 OPF 状态 / 单周期运行点。
hasUncertaintyHandlingFeature
DeterministicOPF; DataDrivenLoadVariation
说明：负荷样本通过在参考负荷 0.9 到 1.1 倍范围内均匀采样生成，但模型本身不是随
机 OPF、鲁棒 OPF 或机会约束 OPF。
hasPowerSystemDomainFeature
TransmissionNetworkOPF; SmartGridOPF
hasSolutionMethodEnhancementFeature
Optimal Power Flow Using Graph Neural Networks
2

LearningAssistedOPF; GraphNeuralNetwork; ImitationLearning; DataDrivenOPF;
LocalScalableArchitecture
hasModelPerformanceFeature
FastComputation; ScalableForLargeSystem; RealTimeSuitable;
LocalComputation; HighSpeedApproximation
hasDemandSideFeature
FixedLoad
4. ModelStructure
Dataproperty 数据属性
hasObjectiveFunction
底层 OPF 目标函数是最小化所有发电机的发电成本，即 minimize sum cm(pm)。其
中 cm(pm) 是发电机 m 的成本函数，通常为二次成本函数。
学习模型的训练目标是最小化 IPOPT 最优解 p* 与 GNN 预测值 Φ(X; H, W) 之间的
误差，论文使用 MSE 训练，并用 relative RMSE 评估。
hasConstraintFunction
底层 ACOPF 约束包括：
1. 有功潮流方程 p = P(v, δ; W)。
2. 无功潮流方程 q = Q(v, δ; W)。
3. 状态变量上下限约束 Xmin ≤ X ≤ Xmax，包括电压幅值、电压相角、有功功率和
无功功率范围。
注意：这些约束用于生成 IPOPT 标签解。GNN 推理阶段主要学习映射关系，并
没有显式硬约束保证。
usesParameter
Graph G = (V, E, W), bus set V, line set E, edge weight W, impedance zij,
Gaussian edge weight wij, adjacency matrix W, node state X = [v, δ, p, q],
voltage magnitude v, voltage angle δ, active power p, reactive power q,
generator set VG, generator selection matrix G, generator cost cm(pm), IPOPT
optimal solution p*, GNN parameters H, filter taps K, number of layers L, node
features F, load pL, qL, reference load, learning rate, batch size。
hasSolutionDetailsSummary
Optimal Power Flow Using Graph Neural Networks
3

论文将电网表示为图，节点是 buses，边是线路，边权由线路阻抗通过 Gaussian
kernel 计算。每个节点的状态包括电压幅值、电压相角、有功功率和无功功率。模型
使用 GNN 作为函数 Φ(X; H, W)，通过模仿学习拟合 IPOPT 得到的 ACOPF 最优发
电机有功出力 p*。GNN 的图卷积层通过邻居信息交换实现局部计算，因此相比普通
MLP 更能利用电网拓扑结构。
hasModelValidationSummary
实验使用 IEEE-30 和 IEEE-118 两个测试系统。负荷样本围绕参考负荷在 0.9 到 1.1 倍
范围内均匀采样。使用 Pandapower 计算潮流状态，使用 DCOPF 得到 sub-optimal
generator configuration，再用 IPOPT 求解 ACOPF 标签 p*。IPOPT 不收敛的样本
被丢弃。最终 IEEE-30 有 8016 个样本，IEEE-118 有 13129 个样本，训练 / 测试比例
为 80% / 20%。训练采用 Adam，learning rate 为 0.001，训练 100 epochs，
batch size 为 128。
hasFindingsSummary
GNN 在 IEEE-30 和 IEEE-118 上均优于 MLP。IEEE-30 上，Global GNN 的 RMSE
为 0.061，Global MLP 为 0.090，Local GNN 为 0.139，Local MLP 为 0.161。
IEEE-118 上，Global GNN 的 RMSE 为 0.00306，Global MLP 为 0.00958，Local
GNN 为 0.03038，Local MLP 为 0.35932。计算时间方面，IPOPT 在 IEEE-30 上
约 2.16 s，在 IEEE-118 上约 18 s；GNN 推理只需几十微秒，论文指出速度超过 10^5
倍，并且在大系统上扩展性更好。
hasStrengthsAndLimitationsSummary
优点是速度极快、结构局部化、可扩展，并且显式利用电网拓扑结构，尤其适合大规
模电网的快速 ACOPF 近似。限制是它依赖 IPOPT 生成训练标签；只预测发电机有功
出力，不输出完整 OPF 变量；推理阶段没有硬性保证 AC 潮流可行性、电压约束或线
路约束一定满足；实验只覆盖 IEEE-30 和 IEEE-118，且负荷样本是合成生成的。
isScenarioSuitability
适合需要快速近似 ACOPF、关注计算速度、可扩展性和图结构学习的场景。
不适合需要严格可行性保证、完整 ACOPF 变量输出、安全约束、RES 不确定性、多
周期调度、需求响应或储能联合优化的场景。
hasFurtherProperty
GNN 具有局部性和可扩展性，参数数量不依赖网络节点数量。论文还强调 GNN 具有
permutation equivariance 和对图扰动的稳定性，因此比普通 MLP 更适合电网这种
图结构数据。
objective property 对象属性
hasObjectiveFunction
Optimal Power Flow Using Graph Neural Networks
4

GenerationCostMinimization; LearningLossMinimization; OPFImitationObjective
hasConstraintFunction
ACPowerFlowConstraint; ReactivePowerFlowConstraint;
OperationalBoundConstraint; VoltageLimitConstraint;
GeneratorPowerConstraint
usesParameter
VoltageMagnitude; VoltageAngle; ActivePower; ReactivePower;
GraphAdjacencyMatrix; LineImpedance; GeneratorCostCoefficient;
GeneratorSelectionMatrix; NeuralNetworkParameter; TrainingDataset
hasMathematicalProblemType
NLP; NonconvexACOPF; SupervisedLearning; ImitationLearning
hasModeledEnergySector
Electricity
Optimal Power Flow Using Graph Neural Networks
5

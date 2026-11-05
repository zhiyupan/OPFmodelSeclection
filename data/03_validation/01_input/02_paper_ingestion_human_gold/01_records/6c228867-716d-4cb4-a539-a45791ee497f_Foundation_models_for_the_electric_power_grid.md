Foundation models for the
electric power grid
1. PaperMetadata
论文与模型基础识别信息
hasModelName
GridFM
GridFM-v0
Grid Foundation Model for Power Flow Applications
hasPaperTitle
Foundation models for the electric power grid
hasPublicationYear
2024
hasDOI
10.1016/j.joule.2024.11.002
hasAuthor
Hendrik F. Hamann; Blazhe Gjorgiev; Thomas Brunschwiler; Leonardo S. A.
Martins; Alban Puech; Anna Varbella; Jonas Weiss; Juan Bernabe-Moreno;
Alexandre Blondin Massé; Seong Lok Choi; Ian Foster; Bri-Mathias Hodge;
Rishabh Jain; Kibaek Kim; Vincent Mai; François Mirallès; Martin De Montigny;
Octavio Ramos-Leaños; Hussein Supreme; Le Xie; El-Nasser S. Youssef;
Arnaud Zinflou; Alexander Belyi; Ricardo J. Bessa; Bishnu Prasad Bhattarai;
Johannes Schmude; Stanislav Sobolevsky
hasInstitution
IBM Research; ETH Zurich; Equilibrium Energy; National Renewable Energy
Laboratory; Argonne National Laboratory; U.S. Department of Energy; INESC
TEC; Harvard University; Hydro-Québec; University of Chicago; University of
Colorado; New York University; Masaryk University; EPFL
2. MotivationAndSolvedProblem
Foundation models for the electric power grid
1

模型提出动机与解决的问题
hasPrimaryPurpose
该模型主要用于构建电力系统领域的 foundation model，即 GridFM。短期版本
GridFM-v0 主要面向 power flow applications，目标是通过 graph neural
networks 和 masked auto-encoder 预训练，在多种电网拓扑和运行条件下学习
power flow 表示，并服务于 power flow、state estimation、optimal power flow、
contingency analysis 等下游任务。
hasMotivation
能源转型、可再生能源、DER、电动汽车、inverter-based resources、气候变化、
老化基础设施和网络安全威胁正在显著增加电网运行、控制和规划的不确定性与复杂
度。传统物理仿真和优化方法在大量场景分析、实时 OPF、N-1 / N-k contingency
analysis、transmission-distribution co-simulation 等任务中计算压力越来越大。已
有 AI/ML 方法虽然有潜力，但通常缺少可迁移性，往往只能针对单一任务和单一系统
配置。论文因此提出发展 Grid Foundation Models，让模型从大量电网数据和拓扑中
自监督学习，并通过少量数据 fine-tune 到不同下游任务。
hasSolvedProblem
这篇论文不是已经实现完整 OPF 模型，而是提出一个 GridFM / GridFM-v0 发展路
线。它试图解决电力系统 AI 模型难以跨任务、跨拓扑、跨 utility 复用的问题。
GridFM-v0 计划通过大规模 power flow 数据预训练，学习节点的 active power、
reactive power、voltage magnitude 和 voltage angle 之间的结构关系，从而加速
power flow、OPF 和 contingency analysis 等计算密集型任务。
hasResearchQuestion
是否可以像语言模型和天气 foundation model 一样，为电力系统构建一个从多源电
网数据、拓扑和运行状态中自监督学习的 GridFM，使其能够通过 fine-tuning 支持
power flow、OPF、contingency analysis、forecasting、dynamic stability、
control operation、planning 和 cybersecurity 等多种下游任务？
hasPrimaryOutput
GridFM-v0 的主要输出包括：
预训练的 graph-based foundation model；节点变量重构结果，包括 p_i、q_i、
v_i、delta_i；power flow surrogate 输出；用于下游任务 fine-tuning 的 grid
representation / embeddings；面向 power flow、OPF、contingency analysis、
state estimation 等任务的快速预测结果。
3. ModelFeature
Foundation models for the electric power grid
2

模型特征标签
hasModelFeature
GridFoundationModel; GridFM; GridFM-v0; PowerFlowFoundationModel;
GraphFoundationModel; SelfSupervisedGridModel
hasPowerFlowFormulationFeature
ACPowerFlow; ACOPF; GNNBasedPowerFlowEmulator;
PhysicsInformedPowerFlowLearning
说明：GridFM-v0 本身不是传统 OPF 公式，而是面向 power flow / OPF 下游任务
的 foundation model。
hasTimeHorizonFeature
StaticOPF; SinglePeriodOPF; FutureDynamicOPF; FutureTimeSeriesForecasting
说明：GridFM-v0 初始版本主要针对单时间步 power flow reconstruction。论文长
期愿景中扩展到多时间步 forecasting、transient and dynamic stability analysis。
hasTemporalResolution
GridFM-v0 未明确固定时间分辨率。长期版本可能处理 PMU 高分辨率实时数据、
weather / load time series 和多时间尺度电网数据。
hasOptimizationHorizon
GridFM-v0：单 power flow 状态 / 单 operating condition。
长期 GridFM：可扩展到多时间步 forecast、planning 和 scenario generation，但
论文未给出固定优化时域。
hasUncertaintyHandlingFeature
ScenarioBasedOPF; ProbabilisticForecastingPotential;
GenerativeScenarioModeling; UncertaintyAwareGridModel
说明：GridFM-v0 不是传统 stochastic OPF；但论文强调 GridFM 可以用于生成场
景、加速 contingency analysis 和支持不确定性下的 grid operation。
hasPowerSystemDomainFeature
TransmissionNetworkOPF; DistributionNetworkOPF;
PowerGridFoundationModel; MultiTopologyGridModel;
GridPlanningAndOperationModel
hasSolutionMethodEnhancementFeature
LearningAssistedOPF; FoundationModel; GraphNeuralNetwork;
MaskedAutoEncoder; PhysicsInformedLearning; SelfSupervisedLearning;
Foundation models for the electric power grid
3

FineTuning; SimulationAcceleration
hasModelPerformanceFeature
FastComputation; ScalableForLargeSystem; GeneralizableAcrossTopologies;
FineTuningAdaptable; ScenarioAnalysisAcceleration; RealTimeSuitablePotential
hasDemandSideFeature
FixedLoad
说明：GridFM-v0 的 power flow 输入会包含负荷 / 节点注入，但它不是需求响应模
型。
4. ModelStructure
模型结构信息
hasObjectiveFunction
GridFM-v0 预训练阶段的目标不是传统 OPF 的发电成本最小化，而是 masked
power flow data reconstruction。论文提出的总损失函数为：
L = L_SCE + L_powerflow
其中 L_SCE 是 scaled cosine error，用于最小化原始图和重构图之间的差异；
L_powerflow 用于确保重构结果满足 power flow equations。
对于下游 OPF 任务，GridFM-v0 可以 fine-tune 到发电成本最小化、可行性检查和
generator power reconstruction 等任务。
hasConstraintFunction
GridFM-v0 主要通过 physics-informed loss 引入 power flow equations，而不是
像传统 OPF 求解器一样显式硬约束求解。相关约束 / 物理条件包括：
AC power flow equations；节点有功 / 无功注入关系；节点电压幅值和相角关系；
拓扑图边约束；线路和变压器边特征；OPF 下游任务中的发电机容量约束、线路约束
和节点电压约束；contingency analysis 中的拓扑扰动约束。
usesParameter
p_i; q_i; v_i; delta_i; grid topology; bus node features; transmission line edge
features; transformer edge features; graph adjacency; masked node variables;
reconstructed node variables; GNN parameters; encoder weights; decoder
weights; L_SCE; L_powerflow; PGLIB-OPF data; IEEE benchmark data;
OPFData; topology perturbations; load perturbations; PMU data; SCADA data;
AMI data; weather data; market data.
Foundation models for the electric power grid
4

hasSolutionDetailsSummary
论文提出 GridFM-v0 的实现路线。第一阶段收集和生成大量 solved power flow
problems，数据来自实际或合成电网拓扑、PGLIB-OPF、IEEE benchmarks、传统
power flow solvers 以及含拓扑和负荷扰动的数据集。第二阶段开发模型架构，将电
网建模为 graph：节点表示 buses，节点变量包括 active power、reactive power、
voltage magnitude、voltage angle；边表示 transmission lines 和 transformers。
模型采用 masked auto-encoder 自监督预训练，任务是从部分 masked 的节点变量
中重构完整 power flow 状态。第三阶段在行业真实数据上验证和调整模型。第四阶
段将 GridFM-v0 fine-tune 到 power flow、OPF、contingency analysis 等下游应
用。图 5 给出了 GridFM-v0 的 roadmap，图 6 展示了 masked input 到
reconstructed input 的 GNN autoencoder 结构。
hasModelValidationSummary
这篇论文是 Perspective / roadmap，不是实验论文，因此没有像普通 OPF 论文那样
给出完整数值算例验证。论文提出未来 GridFM-v0 应先在公开数据上 pre-train 和
test，再与 utility partners 在防火墙后使用真实 operational data 进行验证。论文也
引用已有 GNN power flow solver 和 neural AC-OPF work 作为可行性依据，例如
已有 GNN power flow 模型在预测量上误差小于 1%，以及已有神经 AC-OPF solver
可达到 2 到 4 个数量级 speed-up。
hasFindingsSummary
论文的核心结论是：GridFMs 有潜力填补电力系统计算能力与能源转型需求之间的缺
口。GridFM-v0 被预计可比传统 power flow solvers 快 3 到 4 个数量级，从而支持
更多 contingency scenarios、OPF 场景和不确定性分析。论文还指出，foundation
model 的优势在于：一次预训练后，可以用少量标签数据 fine-tune 到多个下游任务
和不同 utility 的私有数据上，避免每个任务都重新开发专用 AI 模型。
hasStrengthsAndLimitationsSummary
优点：GridFM 具有跨任务、跨拓扑、跨数据源迁移的潜力；可通过 self-supervised
learning 利用大量未标注电网数据；可显著加速 power flow、OPF、contingency
analysis 和 scenario analysis；适合处理能源转型带来的复杂性和不确定性；可通过
fine-tuning 适配不同 utility 的私有数据。
限制：该论文尚未提供完整实现和实验验证；GridFM 需要大量高质量、多样化、可
访问的电网数据；真实电网数据存在隐私、安全和监管限制；foundation model 的可
信度、可解释性、out-of-sample 鲁棒性仍需验证；模型可能被恶意用于推断敏感电
网信息或辅助攻击，因此需要安全治理；GridFM-v0 初期主要面向 power flow，无
法立即覆盖所有电网任务。
isScenarioSuitability
Foundation models for the electric power grid
5

适合：power flow acceleration；AC-OPF 近似求解；contingency analysis；
state estimation；large-scale scenario analysis；multi-topology grid learning；
future forecasting；dynamic stability analysis；control operation；expansion
planning；cybersecurity anomaly detection。
不适合：当前阶段直接作为严格可行的传统 OPF 求解器；不适合没有训练数据和验证
流程的直接工程部署；不适合需要严格数学最优性证明的场景；不适合立即替代所有
EMS / DMS 物理仿真工具。
hasFurtherProperty
该论文最重要的特殊性是：它不是提出一个单一 OPF 公式，而是提出一个 power
grid foundation model 范式。GridFM-v0 的短期目标是 power flow / OPF 相关任
务，长期目标是通过多模态数据和多任务 fine-tuning 覆盖 forecasting、transient
stability、control、planning 和 cybersecurity 等更广泛电力系统应用。
objective property 对象属性
hasObjectiveFunction
PowerFlowReconstructionObjective;
PhysicsInformedLossMinimizationObjective;
ScaledCosineErrorMinimizationObjective;
DownstreamGenerationCostMinimizationObjective;
ContingencyAnalysisAccelerationObjective
hasConstraintFunction
ACPowerFlowEquationConstraint; PhysicsInformedPowerFlowLossConstraint;
NodeFeatureReconstructionConstraint; TopologyConsistencyConstraint;
GeneratorCapacityConstraint; VoltageLimitConstraint; LineFlowLimitConstraint;
ContingencyTopologyPerturbationConstraint
usesParameter
ActivePowerInjection; ReactivePowerInjection; BusVoltageMagnitude;
BusVoltageAngle; GridTopology; TransmissionLineEdge; TransformerEdge;
GraphNodeFeature; MaskedNodeFeature; ReconstructedNodeFeature;
GNNWeight; EncoderParameter; DecoderParameter; PowerFlowLoss; SCELoss;
LoadCondition; TopologyPerturbation; OPFTrainingData
hasMathematicalProblemType
SelfSupervisedLearning; GraphNeuralNetwork; MaskedAutoEncoder;
PhysicsInformedMachineLearning; DownstreamOPF can be NLP or learning-
Foundation models for the electric power grid
6

assisted OPF depending on fine-tuning task
hasModeledEnergySector
Electricity; Wind; PV
Foundation models for the electric power grid
7

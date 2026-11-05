Unbalanced Three-Phase
Optimal Power Flow for Smart
Grids
1. PaperMetadata
论文与模型基础识别信息
hasModelName
Unbalanced Three-Phase OPF, TOPF
hasPaperTitle
Unbalanced Three-Phase Optimal Power Flow for Smart Grids
hasPublicationYear
2011
hasDOI
10.1109/TIE.2011.2106099
hasAuthor
Sergio Bruno; Silvia Lamonaca; Giuseppe Rotondo; Ugo Stecchi; Massimo La
Scala
hasInstitution
Politecnico di Bari, Department of Electrical and Electronic Engineering, Bari,
Italy
2. MotivationAndSolvedProblem
模型提出动机与解决的问题
hasPrimaryPurpose
该模型主要用于智能配电网 DMS 中的不平衡三相最优潮流计算，用来进行负荷削
减、无功调度、电压控制、过载缓解、网损最小化和三相不平衡运行控制。
hasMotivation
Unbalanced Three-Phase Optimal Power Flow for Smart Grids
1

智能电网中的配电管理系统 DMS 需要执行实时或准实时控制，例如无功调度、电压
调节、线路切换、过载处理和安全分析。传统 OPF 多用于输电网，通常基于单相或正
序模型，不能准确描述配电网中常见的三相不平衡、单相负荷、单相微电源和不对称
线路。因此，需要一个面向配电网的 unbalanced three-phase OPF。
hasSolvedProblem
解决的问题是：传统单相 OPF 或正序 OPF 在严重三相不平衡条件下可能低估某一相
导线电流，从而导致物理上某一相已经过载但模型仍认为可行。该 TOPF 模型通过三
相不平衡负荷流和相别约束，能够分别监测和控制 Ia、Ib、Ic，并通过负荷削减或无
功调度缓解过载和降低损耗。
hasResearchQuestion
本文是否可以构建一个基于 OpenDSS 三相不平衡潮流和 quasi-Newton 优化方法的
TOPF，使其适用于智能配电网 DMS 的扩展实时控制，并且比单相 OPF 更准确地处
理三相不平衡和单相微电源？
hasPrimaryOutput
各负荷节点的最优负荷削减量；各相线路电流 Ia、Ib、Ic；正序 / 负序 / 零序电流指
标；无功资源调度量；可控电容器出力；微电源无功输出；节点电压；网损；算法迭
代结果和计算时间。
3. ModelFeature
模型特征标签
hasModelFeature
UnbalancedThreePhaseOPF; DistributionManagementSystemOPF;
SmartGridDMSControl; LoadCurtailmentOPF; ReactivePowerDispatchOPF;
ExtendedRealTimeOPF
hasPowerFlowFormulationFeature
UnbalancedThreePhaseOPF; ACOPF; DistributionOPF
hasTimeHorizonFeature
StaticOPF; SinglePeriodOPF; RealTimeOPF
hasTemporalResolution
约 15–30 min 的扩展实时运行周期
hasOptimizationHorizon
单个运行状态 / 单时段 OPF；可以在 DMS 中每 15–30 min 重复执行。
Unbalanced Three-Phase Optimal Power Flow for Smart Grids
2

hasUncertaintyHandlingFeature
DeterministicOPF
hasPowerSystemDomainFeature
DistributionNetworkOPF; SmartGridOPF; AdvancedDMSOPF;
RadialDistributionFeederOPF
hasSolutionMethodEnhancementFeature
QuasiNewtonMethod; PenaltyFunctionMethod; NumericalSensitivityMethod;
OpenDSSBasedLoadFlow; MATLABOpenDSSCoupling
hasModelPerformanceFeature
ExtendedRealTimeSuitable; HandlesUnbalancedNetwork;
PhaseSpecificSecurityControl; FlexibleObjectiveFunction; CompatibleWithDMS
hasDemandSideFeature
FlexibleLoad; DemandResponse; LoadShedding
4. ModelStructure
模型结构信息
Dataproperty 数据属性
hasObjectiveFunction
论文中的 TOPF 是一个通用框架，可以根据运行目的设置不同目标函数。测试中包
括：最小化负荷削减量以缓解过载；通过相电流约束保证线路不过载；最小化系统网
损；通过负序和零序电流惩罚降低三相不平衡；协调有功负荷削减和无功资源调度。
hasConstraintFunction
包括三相不平衡潮流方程；线路热稳定 / 电流约束；每相电流 Ia、Ib、Ic 上限约束；
正序电流约束；负序和零序不平衡惩罚约束；电压运行范围约束；可控负荷削减上
限；可控电容器无功出力上限；微电源无功输出上下限；控制变量硬上下限。
usesParameter
x; u; Cobj; Cp; f(x,u); g(x,u); Ia; Ib; Ic; Id; Ii; I0; Imax; P_load; Q_load; voltage
magnitude; phase voltage; reactive power output; capacitor bank output;
microgenerator reactive power; alpha penalty factor; lambda step size;
OpenDSS distribution feeder data.
hasSolutionDetailsSummary
Unbalanced Three-Phase Optimal Power Flow for Smart Grids
3

模型将 TOPF 写成非线性优化问题。等式约束是三相不平衡负荷流方程；不等式约束
通过 penalty functions 处理；控制变量通过 hard limits 限定。求解算法使用 quasi-
Newton 方法，并采用 Barzilai-Borwein 类型步长。每次迭代中，MATLAB 负责计算
灵敏度和控制变量更新，OpenDSS 作为三相不平衡配电潮流计算引擎，通过 COM
interface 与 MATLAB 交换数据。
hasModelValidationSummary
论文使用 IEEE 123-bus Radial Distribution Feeder 进行测试。测试 A、B、C 分别
比较正序电流约束、相电流约束和不平衡惩罚对负荷削减结果的影响；测试 D 使用可
控电容器和单相微电源进行无功调度以最小化网损；测试 E 结合无功调度后的负荷削
减。论文还将 TOPF 与单相 OPF 在平衡化测试系统上比较计算时间。
hasFindingsSummary
测试结果表明，只约束正序电流可能导致某一相电流仍然超过热极限，因此在三相不
平衡配电网中不够安全。使用相别电流约束后，TOPF 能够更准确地识别导致过载的
敏感负荷，并减少不必要的削减。无功资源调度可以降低系统损耗并部分改善三相平
衡；在无功调度之后再进行负荷削减，可以比单独负荷削减减少约 30% 的削减量。
计算时间虽然比单相 OPF 更长，但仍然满足 15–30 min 扩展实时运行要求。
hasStrengthsAndLimitationsSummary
优点是能够显式处理三相不平衡、单相负荷、单相微电源和相别安全约束，比传统正
序 OPF 更适合配电网。模型结构灵活，可以更换目标函数和控制变量，也可以接入
OpenDSS 这样的开源三相配电潮流工具。限制是该方法是单时段运行控制模型，不
是多周期调度模型；不处理可再生能源不确定性；penalty function 可能允许小幅约
束违反；计算速度慢于单相 OPF；实际应用依赖 AMI、通信系统和可控设备基础设
施。
isScenarioSuitability
适合：智能配电网 DMS；三相不平衡配电网；单相微电源接入；过载缓解；负荷削
减；无功优化；电压控制；扩展实时运行。
不适合：社区储能容量规划；PV/CES 选址；EV/HVAC 聚合器调度；随机 OPF；长
期规划。
hasFurtherProperty
论文特别强调，智能电表、智能逆变器、微电源、储能、电容器、同步调相机和电力
电子设备都可以成为该 TOPF 框架中的控制资源。该模型的核心价值不是某一个固定
目标函数，而是提供一个适用于不平衡配电网 DMS 的通用三相 OPF 求解框架。
objective property 对象属性
hasObjectiveFunction
Unbalanced Three-Phase Optimal Power Flow for Smart Grids
4

LoadCurtailmentMinimization; NetworkLossMinimization;
VoltageProfileImprovement; PhaseCurrentSecurity; UnbalanceReduction;
ReactivePowerDispatch
hasConstraintFunction
ThreePhasePowerFlowConstraint; PhaseCurrentLimitConstraint;
ThermalLimitConstraint; VoltageLimitConstraint; ReactivePowerLimitConstraint;
LoadCurtailmentLimitConstraint; ControlVariableBoundConstraint;
PenaltyFunctionConstraint
usesParameter
Pd; Qd; Vm; Va; Ia; Ib; Ic; Id; Ii; I0; Imax; Qg; LoadCurtailment;
CapacitorReactivePower; MicrogeneratorReactivePower; PenaltyWeight;
OpenDSSFeederData
hasMathematicalProblemType
NLP; NonlinearUnconstrainedOptimizationAfterPenalty;
QuasiNewtonOptimization
hasModeledEnergySector
Electricity; PV
Unbalanced Three-Phase Optimal Power Flow for Smart Grids
5

Probabilistically Robust AC
Optimal Power Flow
1. PaperMetadata
hasModelName
Probabilistically Robust AC-OPF with Scenario with Certificates
也可写作 SwC-AC-OPF
hasPaperTitle
Probabilistically Robust AC Optimal Power Flow
hasPublicationYear
2019
hasDOI
10.1109/TCNS.2019.2921300
hasAuthor
Mohammadreza Chamanbaz; Fabrizio Dabbene; Constantino M. Lagoa
hasInstitution
Singapore University of Technology and Design; CNR-IEIIT; Penn State
University
2. MotivationAndSolvedProblem
hasPrimaryPurpose
提出一种概率鲁棒 AC-OPF 方法，在存在不确定负荷和不确定可再生能源出力的情况
下，最小化常规机组发电成本，同时以预先给定的概率保证发电和输电约束被满足。
hasMotivation
现代电网中风电、光伏等可再生能源比例增加，负荷也可能显著波动。传统 OPF 调度
通常基于预测值，是一种比较“刚性”的调度方式，在实际不确定环境下可能导致线路
过载、约束违反甚至连锁故障。完全鲁棒优化虽然可以保证所有不确定场景都安全，
但过于保守。因此，论文采用概率鲁棒思想：允许一个很小、明确可控的约束违反风
险。
Probabilistically Robust AC Optimal Power Flow
1

hasSolvedProblem
解决含不确定负荷和不确定 RES 的 AC-OPF 调度问题。该方法不要求对不确定性进
行保守参数化，而是使用 scenario with certificates 方法，在随机场景样本上构造
convexified AC-OPF，并给出约束违反概率的先验保证。
hasResearchQuestion
在不确定负荷和可再生能源出力下，能否通过 convex relaxation 和 scenario with
certificates 构造一个比传统鲁棒方法更少保守、计算更高效、并带概率约束违反保证
的 AC-OPF 调度方法？
hasPrimaryOutput
输出包括常规发电机的 nominal active power PG、发电机电压幅值 |V|、
deployment vector / distribution vector α，以及运行时根据实际不确定性调整后的
发电机有功出力。对于每个不确定场景，还存在对应的 certificate state variables，
例如 QG 和 W，用于证明该场景下存在满足约束的系统状态。
3. ModelFeature
hasModelFeature
ProbabilisticallyRobustOPF; ChanceConstrainedOPF; ScenarioWithCertificates;
ConvexRelaxedACOPF; RenewableUncertaintyHandling
hasPowerFlowFormulationFeature
ACOPF; SDPRelaxedACOPF
hasTimeHorizonFeature
StaticOPF; SinglePeriodOPF
说明：论文在 24 小时需求曲线上逐小时重复求解，但每次 OPF 本身是单周期 AC-
OPF，不是多周期动态 OPF。
hasTemporalResolution
1 h
说明：数值实验使用 24-hour demand pattern，并对每个小时求解 OPF。
hasOptimizationHorizon
单小时运行点。实验覆盖 24 h，但不是一次性 24 h 多周期优化。
hasUncertaintyHandlingFeature
Probabilistically Robust AC Optimal Power Flow
2

ProbabilisticOPF; RobustOPF; ChanceConstrainedOPF; ScenarioBasedOPF;
RenewableUncertaintyHandling; LoadUncertaintyHandling
hasPowerSystemDomainFeature
TransmissionNetworkOPF; RenewableIntegratedPowerSystem
hasSolutionMethodEnhancementFeature
ConvexRelaxation; SDPRelaxation; ScenarioWithCertificates;
RandomizedOptimization; MonteCarloValidation; YALMIP; Mosek
hasModelPerformanceFeature
ProbabilisticGuarantee; LowConstraintViolationRisk;
LessConservativeThanParameterizedRobustOPF;
ComputationallyEfficientComparedWithPriorScenarioACOPF
hasDemandSideFeature
FixedLoad
4. ModelStructure
Dataproperty 数据属性
hasObjectiveFunction
主要目标是最小化常规发电机的发电成本：
minimize sum fk(PGk)
为了鼓励 SDP relaxation 得到低秩解，论文还讨论了 penalized cost，可以加入发电
机无功功率惩罚和部分线路 apparent power loss 惩罚。概率鲁棒版本中目标是在满
足小概率约束违反风险的前提下，最小化 nominal generation cost 或 worst-case
penalized generation cost。
hasConstraintFunction
包括 AC 有功功率平衡约束、AC 无功功率平衡约束、发电机有功出力上下限、发电机
无功出力上下限、deployment vector α 非负且求和为 1、电压幅值上下限、线路电
压差 / 线路容量约束、W = V V* 的 SDP 松弛约束、W positive semidefinite 约束、
不确定负荷和 RES 注入约束、chance constraint 风险约束。
usesParameter
PG, QG, PL, QL, PR, QR, δL, δR, δ, α, V, |V|, θ, W, Wu, Wx, ylm, line admittance,
voltage limit, generator limit, line limit, ΔVmax, ε, β, NSwC, scenario samples,
Probabilistically Robust AC Optimal Power Flow
3

wind penetration level, Pearson distribution parameters, γb, γl, YALMIP,
Mosek。
hasSolutionDetailsSummary
论文首先把 AC-OPF 中的变量区分为 control variables 和 state variables。control
variables 包括常规机组 nominal active power、发电机母线电压幅值和
deployment vector α；state variables 包括无功出力、非发电机节点电压幅值和电
压相角。然后用 W = V V* 将 AC 潮流中的非凸二次项转化为 SDP relaxation，并把
W 分解为 Wu 和 Wx，以区分控制变量和状态变量。最后使用 scenario with
certificates 方法：对不确定性采样，每个样本都有自己的 certificate variables，从
而不需要预设 state variables 关于不确定性的线性函数形式。
hasModelValidationSummary
论文使用 New England 39-bus 系统进行实验。该系统包含 39 个 buses、46 条
lines、10 个常规发电机，并被修改为在 bus 5、6、14 和 17 接入 4 个风电机组。所
有负荷和风电机组均考虑不确定性，总共有 46 个 uncertain parameters。实验使用
24 h demand pattern，误差分布采用 Pearson system，设置 σ = 0.2 × predicted
value，γ = 0，κ = 3.5。概率精度和置信参数设置为 ε = 0.02，β = 1e-15，得到约 5
× 10^5 个 scenario samples。优化问题用 YALMIP 建模，用 Mosek 求解，并用
10000 个 Monte Carlo 样本做后验验证。
hasFindingsSummary
SwC 方法显著降低约束违反风险。Monte Carlo 验证中，SwC 解只有 14 / 10000 个
不可行样本，empirical violation 为 0.0014；而不考虑不确定性的 nominal OPF 有
5374 / 10000 个不可行样本，empirical violation 为 0.5374。与已有线性参数化方
法相比，在 ε = 0.1、β = 1e-10 的比较实验中，SwC 只需要 839 个样本，而对比方
法需要 11838 个样本；SwC 计算时间约 49 分钟，对比方法超过 51 小时；SwC 的平
均 generation cost 为 25280，而对比方法为 25359。结果说明 SwC 在计算复杂
度、约束违反概率和发电成本上都有优势。
hasStrengthsAndLimitationsSummary
优点是能够同时处理负荷不确定性和可再生能源不确定性，提供明确的概率违反风险
保证，并且避免对状态变量关于不确定性的保守线性参数化。限制是原始 AC-OPF 仍
然是 NP-hard，方法依赖 SDP relaxation；理论 exactness 只在特定网络类别下成
立，例如 lossless weakly cyclic network with cycles of size 3 等限制性条件；一
般网络中 W 不一定是 rank-one，因此结果是有效的近似和概率保证，而不是所有情
况下的严格 AC 全局最优解。方法还需要已知或可采样的不确定性概率分布，并且场
景数量在严格风险水平下可能很大。
isScenarioSuitability
Probabilistically Robust AC Optimal Power Flow
4

适合高比例风电 / 可再生能源接入、电网负荷和新能源出力不确定、需要低风险约束
违反保证的 transmission AC-OPF 调度。
不适合纯确定性 OPF、完全实时秒级控制、多周期储能调度、需求响应优化，或没有
不确定性概率信息的场景。
hasFurtherProperty
论文指出该方法可以扩展到 security-constrained OPF。对于 N-1 security
constraints，可以把 outages 也作为随机变量处理，例如为每个设备设置 Bernoulli
outage probability，从而不仅能处理单个设备故障，还可以自然考虑多个设备同时故
障的概率场景。
objective property 对象属性
hasObjectiveFunction
GenerationCostMinimization; RobustCostMinimization;
ConstraintViolationRiskMinimization; PenalizedReactivePowerCost;
PenalizedLineLossCost
hasConstraintFunction
ACPowerBalanceConstraint; ReactivePowerBalanceConstraint;
GeneratorActivePowerLimitConstraint; GeneratorReactivePowerLimitConstraint;
VoltageLimitConstraint; LineCapacityConstraint;
PositiveSemidefiniteConstraint; ChanceConstraint;
DeploymentVectorConstraint
usesParameter
ActivePowerGeneration; ReactivePowerGeneration;
RenewablePowerUncertainty; LoadUncertainty; VoltageMagnitude;
VoltageAngle; ComplexVoltageMatrix; ScenarioSample; RiskLevel;
ConfidenceLevel; DeploymentVector; LineAdmittance; GeneratorLimit;
VoltageLimit; LineLimit
hasMathematicalProblemType
ChanceConstrainedOPF; RobustOptimization; ScenarioBasedOptimization;
SDP; ConvexRelaxation; NonconvexACOPF
hasModeledEnergySector
Electricity; Wind
Probabilistically Robust AC Optimal Power Flow
5

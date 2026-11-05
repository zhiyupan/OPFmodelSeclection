# A Hybrid Data-Driven Method for Fast Solution of Security-Constrained Optimal Power Flow

## 1. PaperMetadata

论文与模型基础识别信息

**hasModelName**

Hybrid Data-Driven Preventive SCOPF

Model-Assisted PD-DDPG SCOPF

Hybrid DRL-SCOPF

**hasPaperTitle**

A Hybrid Data-Driven Method for Fast Solution of Security-Constrained Optimal Power Flow

**hasPublicationYear**

2022

**hasDOI**

10.1109/TPWRS.2022.3150023

**hasAuthor**

Ziming Yan; Yan Xu

**hasInstitution**

Nanyang Technological University, Singapore

---

## 2. MotivationAndSolvedProblem

模型提出动机与解决的问题

**hasPrimaryPurpose**

该模型主要用于快速求解 preventive security-constrained optimal power flow，也就是预防型安全约束最优潮流。目标是在考虑关键故障场景的同时，快速得到经济性较好且满足安全约束的 OPF 调度结果。

**hasMotivation**

传统 SCOPF 需要同时考虑基准场景和多个故障后场景，问题规模很大，求解速度慢。随着可再生能源接入和运行点波动增强，电力系统需要更快速地适应运行状态变化。传统解析方法虽然可以通过 contingency filtering、Benders decomposition、并行计算等方式加速，但在线应用仍然可能太慢。纯监督学习或普通 DRL 方法虽然快，但难以严格满足安全约束，尤其是线路潮流、电压和功率平衡等约束。因此需要一种结合数据驱动速度和经典 SCOPF 物理约束的混合方法。

**hasSolvedProblem**

该模型解决了数据驱动 SCOPF 中“速度快但约束满足不可靠”的问题。它不是单纯训练 DNN 模仿 SCOPF 解，而是把 primal-dual DDPG 和经典 SCOPF 模型结合起来，在离线训练阶段通过 KKT 条件、拉格朗日函数、内点法、稀疏 Jacobian 和 Hessian 来更新 DRL agent。训练完成后，在线阶段只需要输入负荷状态，就可以快速输出 SCOPF 控制变量。

**hasResearchQuestion**

是否可以把经典 SCOPF 物理模型嵌入 DRL 训练过程，通过 KKT 条件和内点法推导 actor gradient，使训练后的 DRL agent 能够实时输出满足安全约束且接近最优的 preventive SCOPF 解？

**hasPrimaryOutput**

主要输出为 preventive SCOPF 的基准场景控制变量：

发电机有功出力 Pg；发电机母线电压设定值 Vg。

同时，通过潮流计算可以得到基准场景和故障场景下的节点电压、线路潮流、约束违反量和运行成本。

---

## 3. ModelFeature

模型特征标签

**hasModelFeature**

PreventiveSCOPF; HybridDataDrivenOPF; ModelAssistedDRL; SecurityConstrainedOPF; FastSCOPFSolver

**hasPowerFlowFormulationFeature**

ACOPF; AC-SCOPF; PreventiveSCOPF

说明：论文使用 AC 潮流方程，包括有功和无功功率平衡方程，并考虑电压幅值、线路潮流和发电机约束。因此它比第一篇论文更接近完整 AC-SCOPF。

**hasTimeHorizonFeature**

StaticOPF; SinglePeriodOPF; RealTimeOPF

**hasTemporalResolution**

论文未明确给出固定时间步长。模型目标是在线快速求解当前运行状态下的 preventive SCOPF。

**hasOptimizationHorizon**

单时段 preventive dispatch；不是多时段 SCOPF。

**hasUncertaintyHandlingFeature**

DeterministicOPF; ScenarioBasedOPF; SecurityConstrainedOPF

说明：论文通过 critical contingencies 考虑故障场景，但不是随机 OPF、鲁棒 OPF 或机会约束 OPF。Monte Carlo 主要用于生成训练运行状态，不等于模型本身是 stochastic OPF。

**hasPowerSystemDomainFeature**

TransmissionNetworkOPF; SecurityConstrainedTransmissionOPF; LargeScalePowerSystemOPF

**hasSolutionMethodEnhancementFeature**

LearningAssistedOPF; DeepReinforcementLearning; PrimalDualDDPG; ModelAssistedGradient; KKTBasedMethod; InteriorPointMethod; SparseJacobianHessian; SupervisedLearningInitialization

**hasModelPerformanceFeature**

FastComputation; RealTimeSuitable; HighOptimality; StrongConstraintCompliance; ScalableForLargeSystem

**hasDemandSideFeature**

FixedLoad

---

## 4. ModelStructure

模型结构信息

**hasObjectiveFunction**

目标函数是总发电成本最小化。论文中的 SCOPF 目标函数通常写为：

min f0(x0, u0)

其中总发电成本为：

f0 = sum_i in SG(ai PGi^2 + bi PGi + ci)

**hasConstraintFunction**

主要约束包括：

基准场景和故障后场景的 AC 有功功率平衡约束；基准场景和故障后场景的 AC 无功功率平衡约束；发电机出力物理限制；节点电压上下限约束；输电线路潮流限制；critical contingency 下的安全约束；DRL 训练中的拉格朗日约束项；KKT 条件；内点法 log-barrier 相关约束。

**usesParameter**

PGi; QGi; PDi; QDi; Vi; delta_ij; Gij; Bij; Sf_i; Sf_max; V_min; V_max; P_Gi_max; generator cost coefficients ai, bi, ci; contingency index k; number of contingencies NC; state variables xk; control variables u0; active load p; reactive load q; action a = [vg, pg]; Lagrange multiplier lambda; inequality multiplier mu; slack variable Z; barrier parameter gamma; Jacobian matrices; Hessian matrices; DNN weights W; DNN biases b.

**hasSolutionDetailsSummary**

论文把 preventive SCOPF 表述为 DRL agent 的约束满足训练问题。DRL agent 的输入是系统状态，也就是有功和无功负荷；输出是 SCOPF 控制动作，也就是发电机电压设定值和有功出力。传统 primal-dual DDPG 需要 reward critic network 和 cost critic network，但这会带来近似误差。该论文用经典 SCOPF 模型替代 critic network，通过拉格朗日函数、KKT 条件和内点法推导 actor gradient。为了降低大规模 SCOPF 的计算负担，论文显式构造了故障场景下的稀疏 Jacobian 和稀疏 Hessian。训练完成后，在线阶段直接由 DRL agent 输出 SCOPF 解。

**hasModelValidationSummary**

论文在 modified IEEE 57-bus system 和 modified IEEE 300-bus system 上进行主要测试，并额外在 ACTIVSg2000 系统上测试更大规模场景。训练数据通过 Monte Carlo 生成，负荷服从高斯分布，标准差为期望值的 5%。测试中选择可能导致过载或过电压的 critical transmission line contingencies。基准方法包括 IPOPT 内点优化器和监督学习方法。比较指标包括运行成本、线路潮流约束违反量、等式约束违反量、无功出力约束违反量和平均求解时间。

**hasFindingsSummary**

结果显示，该混合数据驱动方法可以在保持接近 IPOPT 最优性的同时显著提高在线求解速度。在 57-bus 系统中，proposed hybrid DRL 的平均运行成本略高于 IPOPT，但线路潮流约束违反接近零，平均时间节省超过 99.9%。在 300-bus 系统中，该方法同样比 IPOPT 快很多，并且比监督学习更能满足线路潮流安全约束。在 ACTIVSg2000 系统中，该方法仍能处理更大规模问题，并获得满足线路潮流约束的策略。整体结论是：相比纯监督学习，该方法牺牲少量成本最优性，但显著增强安全约束满足能力和实时应用能力。

**hasStrengthsAndLimitationsSummary**

优点：该模型将经典 AC-SCOPF 模型嵌入 DRL 训练，避免了普通 DRL critic network 的高近似误差；可以考虑基准场景和多个故障后场景；在线阶段速度极快，适合实时应用；在 57-bus、300-bus 和 ACTIVSg2000 系统上表现出较好的可扩展性；相比纯监督学习，安全约束满足能力明显更强。

限制：该方法需要离线训练，训练过程较复杂；只处理 preventive SCOPF，不处理 corrective SCOPF；依赖 critical contingency selection，未枚举所有可能故障；Monte Carlo 负荷采样只是训练数据生成方式，不是真正的概率约束优化；极端未见过的运行状态下仍可能存在泛化风险；部分测试中无功出力约束仍可能出现小幅违反。

**isScenarioSuitability**

适合用于输电网中的快速 preventive SCOPF、N-1 安全约束调度、实时安全校核型 OPF、大规模系统快速近似求解。

不适合直接用于频率动态安全约束、暂态稳定约束、多时段调度、需求响应调度、配电网不平衡三相 OPF 或带显式随机约束的 OPF。

**hasFurtherProperty**

该论文的关键特点是“混合数据驱动”：它不是纯机器学习模型，也不是纯优化模型，而是离线训练阶段使用经典 SCOPF 物理模型指导 DRL agent 学习，在线阶段使用训练好的 agent 快速输出调度决策。它的核心价值在于把 SCOPF 的约束信息通过 KKT 和稀疏导数结构传递给神经网络训练过程。

---

## 5. objective property 对象属性

**hasObjectiveFunction**

GenerationCostMinimizationObjective

**hasConstraintFunction**

ACPowerBalanceConstraint; ActivePowerBalanceConstraint; ReactivePowerBalanceConstraint; GeneratorCapacityConstraint; VoltageMagnitudeLimitConstraint; BranchFlowLimitConstraint; ContingencySecurityConstraint; KKTConditionConstraint; InteriorPointBarrierConstraint

**usesParameter**

ActivePowerGeneration; ReactivePowerGeneration; ActiveLoadDemand; ReactiveLoadDemand; BusVoltageMagnitude; BusVoltageAngle; NetworkAdmittanceMatrix; Conductance; Susceptance; BranchPowerFlow; BranchFlowLimit; GeneratorCostCoefficient; GeneratorLimit; VoltageLimit; ContingencyIndex; LagrangeMultiplier; SlackVariable; JacobianMatrix; HessianMatrix; DRLActorParameter

**hasMathematicalProblemType**

NLP; NonconvexACSCOPF; KKT-based primal-dual interior point training; DRL policy inference for online application

**hasModeledEnergySector**

Electricity
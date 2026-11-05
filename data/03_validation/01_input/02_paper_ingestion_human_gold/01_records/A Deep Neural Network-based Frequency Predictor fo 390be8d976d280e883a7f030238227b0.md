# A Deep Neural Network-based Frequency Predictor for Frequency-Constrained Optimal Power Flow

## 1. PaperMetadata

论文与模型基础识别信息

**hasModelName**

DNN-FCOPF

Deep Neural Network-based Frequency-Constrained Optimal Power Flow

**hasPaperTitle**

A Deep Neural Network-based Frequency Predictor for Frequency-Constrained Optimal Power Flow

**hasPublicationYear**

2025

**hasDOI**

10.1109/IAS62731.2025.11061730

**hasAuthor**

Fan Jiang; Xingpeng Li; Pascal Van Hentenryck

**hasInstitution**

University of Houston; Georgia Institute of Technology

---

## 2. MotivationAndSolvedProblem

模型提出动机与解决的问题

**hasPrimaryPurpose**

该模型主要用于在 OPF 调度中加入频率稳定约束，尤其是同时考虑 RoCoF 和 frequency nadir，使实时调度结果不仅经济，而且能满足低惯量电力系统的频率安全要求。

**hasMotivation**

现代电力系统由于低惯量特征增强，频率稳定问题更加突出。传统 OPF 只考虑经济调度和静态潮流约束，不能保证扰动后的频率安全。精确计算 RoCoF 和频率最低点需要复杂的时域动态仿真，计算量大，不适合实时 FCOPF。已有线性 RoCoF 约束和简化频率最低点约束虽然快，但精度不足。因此论文提出用 DNN 学习复杂频率响应，并把 DNN 频率预测器嵌入 FCOPF 中。

**hasSolvedProblem**

该模型解决了频率约束 OPF 中“频率响应计算太复杂、简化约束又不够准确”的问题。它用 PSCAD/EMTDC 时域电磁暂态仿真生成训练数据，训练 DNN 同时预测 RoCoF 和 frequency nadir，再把 DNN 通过混合整数线性约束形式嵌入 OPF，使 OPF 能在较短时间内得到满足频率稳定要求的调度结果。

**hasResearchQuestion**

是否可以用 EMT 仿真数据训练一个 DNN 频率预测器，同时准确预测 RoCoF 和 frequency nadir，并将其嵌入 FCOPF，使实时 OPF 调度兼顾经济性、求解速度和频率稳定性？

**hasPrimaryOutput**

主要输出包括：

发电机有功出力 Pg；线路有功潮流 Pk；节点相角 theta；DNN 预测的 RoCoF；DNN 预测的 frequency nadir；满足频率约束的 OPF 调度结果。

---

## 3. ModelFeature

模型特征标签

**hasModelFeature**

Frequency-ConstrainedOPF; DNN-FCOPF; LearningAssistedOPF; FrequencySecurityAwareOPF; RealTimeDispatchOPF

**hasPowerFlowFormulationFeature**

LinearizedPowerFlowOPF; DCOPF-likeOPF; FrequencyConstrainedOPF

说明：论文虽然使用 OPF / FCOPF 表述，但约束中主要使用有功功率平衡和线性线路潮流关系：

Pk = (theta_from - theta_to) / xk

因此它不是完整 AC-OPF，而是偏线性化 / DC 潮流形式的 FCOPF。

**hasTimeHorizonFeature**

StaticOPF; SinglePeriodOPF; RealTimeOPF

**hasTemporalResolution**

论文背景中提到实时 OPF 通常约每 5 分钟运行一次，但该模型实验本身没有固定设置具体时间步长。

**hasOptimizationHorizon**

单时段实时调度；论文未给出多时段优化时域。

**hasUncertaintyHandlingFeature**

DeterministicOPF; ScenarioBasedOPF

说明：论文考虑不同负荷水平和发电机跳闸位置作为仿真场景，但没有建立随机 OPF、鲁棒 OPF 或机会约束 OPF。

**hasPowerSystemDomainFeature**

TransmissionNetworkOPF; LowInertiaPowerSystemOPF; FrequencyStabilityConstrainedPowerSystem

**hasSolutionMethodEnhancementFeature**

LearningAssistedOPF; DNNEmbeddedConstraint; MILPReformulation; MixedIntegerLinearEncoding; GurobiBasedMethod

**hasModelPerformanceFeature**

FastComputation; HighAccuracy; RealTimeSuitable; FrequencySecurityEnhanced

**hasDemandSideFeature**

FixedLoad

---

## 4. ModelStructure

模型结构信息

**hasObjectiveFunction**

目标函数是发电成本最小化。论文使用二次发电成本函数：

C(Pg_i) = sum_i(c2_i Pg_i^2 + c1_i Pg_i + c0_i)

**hasConstraintFunction**

主要约束包括：

功率平衡约束；线性线路潮流约束；发电机有功出力上下限约束；线路热稳定 / 潮流容量约束；DNN 隐藏层 ReLU 线性化约束；DNN 预测 RoCoF 下限约束；DNN 预测 frequency nadir 下限约束。

其中 DNN-FCOPF 的核心频率约束是：

RoCoF_DNN >= RoCoF_threshold

f_nadir_DNN >= f_threshold

**usesParameter**

Pg; Pload; Pk; theta; xk; generator cost coefficients c2, c1, c0; Pg_min; Pg_max; Pk_min; Pk_max; f0; Hsys; Pbase; Ploss; RoCoF_threshold; f_threshold; DNN weights Wm; DNN biases bm; ReLU binary variable Bm; lower bound hl; upper bound hu; tripped generator location; generator real power outputs; load real power values.

**hasSolutionDetailsSummary**

论文首先用 PSCAD/EMTDC 建立电磁暂态仿真模型，生成大量不同负荷、不同发电机出力和不同跳闸位置下的频率响应数据。然后训练一个 DNN 频率预测器，输入为所有发电机有功出力、所有负荷有功功率以及跳闸发电机位置，输出为 RoCoF 和 frequency nadir。由于 ReLU 激活函数是非线性的，论文将 DNN 预测器重写成混合整数线性约束，并嵌入 FCOPF 中。最终模型在 Python 3.9 中实现，并使用 Gurobi 求解。

**hasModelValidationSummary**

模型在 modified IEEE 9-bus system 上验证。论文将 bus 1、bus 2、bus 3 上的发电机拆分为多个机组，以构造不同跳闸场景。PSCAD/EMTDC 用于生成训练数据和作为频率响应验证基准。比较模型包括：传统无频率约束 T-OPF、只考虑线性 RoCoF 的 L-FCOPF，以及本文提出的 DNN-FCOPF。测试场景包括正常负荷变化场景和 120% 高负荷场景。

**hasFindingsSummary**

结果显示，DNN-FCOPF 比传统 T-OPF 和线性 L-FCOPF 更能准确保证频率安全。在 G21 跳闸场景中，DNN-FCOPF 的 RoCoF 误差约 1.2%，frequency nadir 误差约 0.02%，而 L-FCOPF 的 RoCoF 误差很高。在 120% 高负荷场景中，DNN-FCOPF 的 RoCoF 误差约 7.07%，frequency nadir 误差约 0.05%，明显优于线性 FCOPF。代价是 DNN-FCOPF 的求解时间和运行成本略高，但频率安全性显著提高。

**hasStrengthsAndLimitationsSummary**

优点：该模型能同时考虑 RoCoF 和 frequency nadir；训练数据来自 EMT 仿真，比简单机电暂态近似更可靠；DNN 被嵌入 OPF 约束中，而不是直接端到端预测 OPF 解，因此可行性更强；相比传统线性频率约束，频率响应预测精度更高。

限制：测试系统较小，仅为 modified IEEE 9-bus system；潮流模型更接近线性 DC-OPF，而不是完整 AC-OPF；DNN 预测效果依赖训练数据覆盖范围；混合整数约束可能在大规模系统上带来更高求解负担；论文将大规模可再生能源和 grid-following / grid-forming 控制策略作为未来工作，而不是当前模型已完成内容。

**isScenarioSuitability**

适合用于低惯量电力系统、实时频率安全调度、发电机跳闸后的频率稳定约束 OPF。

不适合直接作为完整 AC-OPF、多时段 OPF、配电网 OPF、需求响应 OPF 或大规模新能源不确定性 OPF 的模型。

**hasFurtherProperty**

该论文的重要特点是：不是用 DNN 直接替代整个 OPF，而是只用 DNN 替代复杂频率响应计算，并将预测器作为约束嵌入 OPF。这使模型比纯机器学习 OPF 更有物理约束意识。

---

## 5. objective property 对象属性

**hasObjectiveFunction**

GenerationCostMinimizationObjective

**hasConstraintFunction**

PowerBalanceConstraint; LinearPowerFlowConstraint; GeneratorActivePowerLimitConstraint; LineThermalLimitConstraint; DNNReLUEncodingConstraint; RoCoFConstraint; FrequencyNadirConstraint

**usesParameter**

ActivePowerGeneration; ActiveLoadDemand; LineActivePowerFlow; VoltageAngle; LineReactance; GeneratorCostCoefficient; GeneratorPowerLimit; LineFlowLimit; RoCoFThreshold; FrequencyNadirThreshold; DNNWeight; DNNBias; BinaryActivationVariable; TrippedGeneratorLocation

**hasMathematicalProblemType**

QP for base T-OPF and L-FCOPF; MIQP for DNN-FCOPF if quadratic generation cost is retained; MILP-style reformulation is used for the embedded DNN frequency predictor.

**hasModeledEnergySector**

Electricity
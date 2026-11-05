# Chance-Constrained OPF: A Distributed Method With Confidentiality Preservation

## hasModelName

Distributed Confidentiality-Preserving Chance-Constrained OPF Model

## hasPaperTitle

Chance-Constrained OPF: A Distributed Method With Confidentiality Preservation

## hasPublicationYear

2022 online publication / 2023 journal issue

## hasDOI

10.1109/TPWRS.2022.3200941

## hasAuthor

Mengshuo Jia

Gabriela Hug

Yifan Su

Chen Shen

## hasInstitution

Department of Information Technology and Electrical Engineering, ETH Zurich, Zurich, Switzerland

Department of Electrical Engineering, Tsinghua University, Beijing, China

# 2. MotivationAndSolvedProblem

## hasPrimaryPurpose

The model is mainly used to solve the global chance-constrained optimal power flow problem of a multi-regional interconnected grid in a distributed and confidentiality-preserving manner.

## hasMotivation

The motivation is that increasing wind power integration creates uncertainty in power system operation, while interconnection among regional grids can reduce curtailment and improve economic efficiency. However, in a multi-regional interconnected grid, regional ISOs may refuse to share confidential data such as generation costs, load data, system topology, line parameters, and scheduled generation outputs. Existing centralized CC-OPF methods are unsuitable for this setting, and existing privacy-preserving approaches can cause optimality loss or computational burden.

## hasSolvedProblem

The model solves the problem of how multiple regional ISOs can obtain the exact global optimal dispatchable generation results for their own regions without disclosing confidential regional data to other ISOs.

## hasResearchQuestion

Can a distributed chance-constrained OPF method solve the global CC-OPF problem of a multi-regional interconnected grid while preserving each regional ISO’s confidential information and maintaining the same optimal solution as the centralized benchmark?

## hasPrimaryOutput

The primary outputs are optimal dispatchable generation schedules for each region and time slot, encrypted and decrypted regional generation variables, optimal objective values, chance-constrained feasible dispatch results, and line-flow or voltage security results under wind power uncertainty.

# 3. ModelFeature

## hasModelFeature

Chance-Constrained OPF

Distributed CC-OPF

Confidentiality-Preserving OPF

Transformation-Based Encryption OPF

Multi-Regional Interconnected Grid OPF

Wind-Uncertainty-Aware OPF

Region-Wise Distributed OPF

Privacy-Preserving Global Dispatch

## hasPowerFlowFormulationFeature

LinearizedACOPF

DecoupledLinearizedPowerFlow

ChanceConstrainedLinearizedOPF

DLPFBasedOPF

## hasTimeHorizonFeature

MultiPeriodOPF

DayAheadOPF

TimeSlotBasedOPF

MultiTimeSlotCCOPF

## hasTemporalResolution

Not explicitly fixed in the general model

24 time slots in the case study

## hasOptimizationHorizon

24 time slots in the day-ahead dispatch case study

## hasUncertaintyHandlingFeature

ChanceConstrainedOPF

StochasticOPF

ProbabilisticOPF

GaussianMixtureModelUncertainty

SingleChanceConstraint

JointChanceConstraintExtension

WindPowerUncertainty

## hasPowerSystemDomainFeature

TransmissionNetworkOPF

MultiRegionalInterconnectedGridOPF

LargeScalePowerSystemOPF

WindIntegratedPowerSystem

RegionalISOCoordinatedOPF

InterconnectedGridDispatch

## hasSolutionMethodEnhancementFeature

DistributedOptimization

ConfidentialityPreservation

TransformationBasedEncryption

PrivacyPreservingAAC

AcceleratedAverageConsensus

DistributedLinearEquationSolver

QuantileBasedChanceConstraintConversion

GMMBasedUncertaintyModeling

YALMIPBasedOptimization

GurobiSolver

## hasModelPerformanceFeature

HighAccuracy

NoOptimalityLoss

ConfidentialityPreserving

ScalableForLargeSystem

NoParameterTuning

RobustConvergence

DistributedComputingSuitable

DayAheadDispatchSuitable

## hasDemandSideFeature

FixedLoad

# 4. ModelStructure

## hasObjectiveFunction

GenerationCostMinimization

QuadraticGenerationCostMinimization

MultiRegionalDispatchCostMinimization

GlobalOperationCostMinimization

ChanceConstrainedEconomicDispatch

## hasConstraintFunction

SupplyDemandChanceConstraint

StateChanceConstraint

LineFlowChanceConstraint

VoltageChanceConstraint

SingleChanceConstraint

JointChanceConstraintExtension

QuantileBasedDeterministicEquivalentConstraint

DispatchableGenerationCapacityConstraint

GeneratorUpperOutputLimitConstraint

GeneratorLowerOutputLimitConstraint

GeneratorRampUpConstraint

GeneratorRampDownConstraint

MultiPeriodRampRateConstraint

DecoupledLinearizedPowerFlowConstraint

LinearStateMappingConstraint

NodalVoltageStateConstraint

LineFlowStateConstraint

PowerInjectionMappingConstraint

RegionalStateConstraint

EncryptedDecisionVariableTransformationConstraint

TransformationBasedEncryptionConstraint

EquivalentModifiedCapacityConstraint

EquivalentModifiedRampRateConstraint

MaskedCoefficientMatrixConstraint

PrivacyPreservingDataAggregationConstraint

AACConsensusConstraint

PPAACConsensusConstraint

EncryptedGlobalQPReconstructionConstraint

## usesParameter

M — set of regions

T — set of time slots

G — set of dispatchable generators

W — set of non-dispatchable wind farms

D — set of loads

S — set of system states

Gn — set of dispatchable generators in region n

Wn — set of non-dispatchable wind farms in region n

Dn — set of loads in region n

Sn — set of system states in region n

n — region index

m — region index

t — time-slot index

i — state index

gn_t — dispatchable active power generation in region n at time t

wn_t — active wind power output in region n at time t

reactive wind power — reactive wind power output

omega_t — aggregated active wind power at time t

wt — wind power collection across all regions and time slots

dn_t — active load in region n at time t

reactive load — reactive load demand

sn_t — system state in region n at time t

sn_i_t — state i in region n at time t

s_n_i_plus — upper bound of state i in region n

Omega_n_i_t — aggregated random variable in the state chance constraint

Vn — unknown voltage magnitude vector in region n

theta_n — unknown voltage angle vector in region n

Pn — nodal active power injection vector in region n

Qn — nodal reactive power injection vector in region n

F0 — original objective function value

x — global decision variable vector

xn — regional decision variable vector of region n

Q — global quadratic cost matrix

Qn — regional quadratic cost matrix of region n

C — global linear cost vector

cn — regional linear cost vector of region n

In — regional quadratic cost coefficient matrix

Kn — regional linear cost coefficient vector

A — global constraint matrix

An — regional constraint matrix of region n

B — global right-hand-side constraint vector

J_n — coefficient matrix for generation capacity constraints

E_n — coefficient matrix for ramp-rate constraints

G_n_plus — upper generation limit vector

G_n_minus — lower generation limit vector

R_n_plus — upward ramp-rate limit vector

R_n_minus — downward ramp-rate limit vector

U_n — state mapping matrix

Phi_n — coupled coefficient matrix of region n

K_n — power balance constraint matrix

Upsilon — right-hand-side vector of the supply-demand chance constraint

Delta — right-hand-side vector of the state chance constraint

epsilon_b — risk level of the supply-demand chance constraint

alpha_S — risk level of the state chance constraint

P_inverse_omega_t — quantile of aggregated wind power

P_inverse_Omega_n_i_t — quantile of the aggregated state-related random variable

GMM — Gaussian mixture model

CDF — cumulative distribution function

quantile — quantile value used in chance-constraint conversion

wind power distribution — probability distribution of wind power uncertainty

historical wind data — historical wind power data used for uncertainty modeling

Mn — encryption matrix of region n

M_encryption — global block-diagonal encryption matrix

x_bar_n — encrypted regional decision variable of region n

x_bar — encrypted global decision variable

Q_bar — encrypted quadratic cost matrix

A_bar — encrypted constraint matrix

G_bar_n_plus — encrypted upper generation limit of region n

G_bar_n_minus — encrypted lower generation limit of region n

R_bar_n_plus — encrypted upward ramp-rate limit of region n

R_bar_n_minus — encrypted downward ramp-rate limit of region n

phi_n_plus — positive definite diagonal encryption matrix for upper capacity constraints

phi_n_minus — positive definite diagonal encryption matrix for lower capacity constraints

zeta_n_t_plus — encryption matrix for upward ramp-rate constraints at time t

zeta_n_t_minus — encryption matrix for downward ramp-rate constraints at time t

W_Q_n — private encryption matrix for distributed linear equation solving

W_P_n — private encryption matrix for distributed linear equation solving

B_Q_n — inverse DLPF submatrix related to reactive-power equations

B_P_n — inverse DLPF submatrix related to active-power equations

B_bar_Q_n — encrypted B_Q_n matrix

B_bar_P_n — encrypted B_P_n matrix

y_n_0 — initial value of ISO n in the AAC or PP-AAC algorithm

delta_n_k — random noise generated by ISO n at iteration k

pi_n_k — noise-difference term in the PP-AAC algorithm

Na — number of regions

Hn — number of decision variables in region n

H — total number of global decision variables

Nq — number of quadratic terms

Nl — number of linear terms

New England 39-bus case — test system used in the case study

IEEE 57-bus case — test system used in the case study

PEGASE 89-bus case — test system used in the case study

IEEE 118-bus case — test system used in the case study

Illinois 200-bus case — test system used in the case study

IEEE 300-bus case — test system used in the case study

PEGASE 1354-bus case — test system used in the case study

Eastern Wind Integration Dataset — wind power dataset used in the case study

YALMIP — MATLAB-based optimization modeling tool

Gurobi 9.5.1 — optimization solver

NumericFocus — Gurobi numerical robustness setting

## hasSolutionDetailsSummary

The paper formulates a multi-period chance-constrained OPF problem for a multi-regional interconnected grid under wind power uncertainty. First, the AC-related system states are represented using a decoupled linearized power flow model. Then the single chance constraints for supply-demand balance and system states are converted into deterministic constraints through quantile calculation based on Gaussian mixture models. After conversion, the CC-OPF becomes a quadratic programming problem. To preserve confidentiality, each regional ISO applies transformation-based encryption to its decision variables, objective coefficients, and constraint coefficients. Additional equivalent modifications are used to protect generation capacity and ramp-rate bounds. The method further uses a fast confidentiality-preserving distributed linear equation solver to obtain coupled coefficient matrices, and PP-AAC is used for privacy-preserving aggregation of confidential regional data. The final encrypted global QP is solved by each ISO, and each ISO decrypts only its own optimal dispatch using its private encryption matrix.

## hasModelValidationSummary

The model is validated on the New England 39-bus case, IEEE 57-bus case, PEGASE 89-bus case, IEEE 118-bus case, Illinois 200-bus case, IEEE 300-bus case, and PEGASE 1354-bus case. Each test system is manually divided into multiple regions. Two load levels are considered, where the high load level is twice the low load level. Wind farms are added to each test system using historical data from the Eastern Wind Integration Dataset. The case study uses 24 time slots for day-ahead dispatch. The risk limit for the supply-demand chance constraint is set to 10^-4, and the probability limit for line-flow chance constraints is set to 0.95. Experiments are implemented in MATLAB 2020b with YALMIP and solved using Gurobi 9.5.1.

## hasFindingsSummary

The case studies show that the proposed distributed CC-OPF method achieves very high accuracy compared with the centralized benchmark. Across different system sizes and load levels, the relative error of the objective value is less than 2 × 10^-8. The proposed fast distributed method for solving linear equation systems outperforms the accelerated projection-based consensus benchmark in both accuracy and computational efficiency. The total computational time of the proposed CC-OPF method is higher than the centralized benchmark because confidentiality preservation and distributed coordination introduce additional overhead, but the time growth remains acceptable for day-ahead dispatch. Compared with state-of-the-art obfuscation methods, the proposed method achieves significantly smaller optimality gaps and does not require a third party or prior knowledge of the optimal objective value.

## hasStrengthsAndLimitationsSummary

The main strength of the model is that it enables regional ISOs to solve a global CC-OPF problem in a distributed way while preserving confidential data such as generation costs, load data, grid topology, line parameters, capacities, ramp rates, and regional scheduled generation. The transformation-based encryption method theoretically preserves the optimality of the corresponding benchmark and avoids the quantization error of partially homomorphic encryption and the optimality loss of differential privacy. The proposed method also does not require manual parameter tuning and has robust convergence. However, the model relies on a decoupled linearized power flow model and therefore cannot directly handle full AC constraints. Its confidentiality-preserving and distributed features introduce extra computational cost compared with the centralized benchmark. The method also has a specific limitation when a single-period OPF contains a region with only one dispatchable generator under a global power balance constraint.

## isScenarioSuitability

True / scenario-applicable

## MonteCarlo

False

## hasFurtherProperty

1. The proposed method is designed for multi-regional interconnected grids with multiple regional ISOs.
2. The model protects generation costs, generator capacities, ramp-rate limits, load data, grid topology, line parameters, and scheduled generation outputs.
3. The chance constraints are converted using quantile calculation under Gaussian mixture model wind uncertainty.
4. The converted CC-OPF becomes a quadratic programming problem.
5. The proposed method uses transformation-based encryption instead of partially homomorphic encryption or differential privacy.
6. The method can be extended to AGC-aware CC-OPF when AGC participation factors are deterministic.
7. The method can also be extended to joint-chance-constrained OPF.
8. Future work includes extension to full AC-based OPF and multi-carrier multi-agent energy systems.

# Objective Property

## hasObjectiveFunction

GenerationCostMinimization

QuadraticGenerationCostMinimization

LinearGenerationCostMinimization

GlobalOperationCostMinimization

MultiRegionalDispatchCostMinimization

ChanceConstrainedEconomicDispatch

WindUncertaintyAwareDispatch

## hasConstraintFunction

SupplyDemandChanceConstraint

StateChanceConstraint

LineFlowChanceConstraint

VoltageChanceConstraint

SingleChanceConstraint

JointChanceConstraintExtension

QuantileBasedDeterministicEquivalentConstraint

DispatchableGenerationCapacityConstraint

GeneratorUpperOutputLimitConstraint

GeneratorLowerOutputLimitConstraint

GeneratorRampUpConstraint

GeneratorRampDownConstraint

MultiPeriodRampRateConstraint

DecoupledLinearizedPowerFlowConstraint

LinearStateMappingConstraint

NodalVoltageStateConstraint

LineFlowStateConstraint

PowerInjectionMappingConstraint

RegionalStateConstraint

EncryptedDecisionVariableTransformationConstraint

TransformationBasedEncryptionConstraint

EquivalentModifiedCapacityConstraint

EquivalentModifiedRampRateConstraint

MaskedCoefficientMatrixConstraint

PrivacyPreservingDataAggregationConstraint

AACConsensusConstraint

PPAACConsensusConstraint

EncryptedGlobalQPReconstructionConstraint

## usesParameter

M — set of regions

T — set of time slots

G — set of dispatchable generators

W — set of non-dispatchable wind farms

D — set of loads

S — set of system states

Gn — set of dispatchable generators in region n

Wn — set of non-dispatchable wind farms in region n

Dn — set of loads in region n

Sn — set of system states in region n

n — region index

m — region index

t — time-slot index

i — state index

gn_t — dispatchable active power generation in region n at time t

wn_t — active wind power output in region n at time t

omega_t — aggregated active wind power at time t

wt — wind power collection across all regions and time slots

dn_t — active load in region n at time t

sn_t — system state in region n at time t

sn_i_t — state i in region n at time t

s_n_i_plus — upper bound of state i in region n

Omega_n_i_t — aggregated random variable in the state chance constraint

Vn — unknown voltage magnitude vector in region n

theta_n — unknown voltage angle vector in region n

Pn — nodal active power injection vector in region n

Qn — nodal reactive power injection vector in region n

F0 — original objective function value

x — global decision variable vector

xn — regional decision variable vector of region n

Q — global quadratic cost matrix

Qn — regional quadratic cost matrix of region n

C — global linear cost vector

cn — regional linear cost vector of region n

In — regional quadratic cost coefficient matrix

Kn — regional linear cost coefficient vector

A — global constraint matrix

An — regional constraint matrix of region n

B — global right-hand-side constraint vector

J_n — coefficient matrix for generation capacity constraints

E_n — coefficient matrix for ramp-rate constraints

G_n_plus — upper generation limit vector

G_n_minus — lower generation limit vector

R_n_plus — upward ramp-rate limit vector

R_n_minus — downward ramp-rate limit vector

U_n — state mapping matrix

Phi_n — coupled coefficient matrix of region n

K_n — power balance constraint matrix

Upsilon — right-hand-side vector of the supply-demand chance constraint

Delta — right-hand-side vector of the state chance constraint

epsilon_b — risk level of the supply-demand chance constraint

alpha_S — risk level of the state chance constraint

P_inverse_omega_t — quantile of aggregated wind power

P_inverse_Omega_n_i_t — quantile of the aggregated state-related random variable

GMM — Gaussian mixture model

CDF — cumulative distribution function

quantile — quantile value used in chance-constraint conversion

historical wind data — historical wind power data used for uncertainty modeling

Mn — encryption matrix of region n

M_encryption — global block-diagonal encryption matrix

x_bar_n — encrypted regional decision variable of region n

x_bar — encrypted global decision variable

Q_bar — encrypted quadratic cost matrix

A_bar — encrypted constraint matrix

G_bar_n_plus — encrypted upper generation limit of region n

G_bar_n_minus — encrypted lower generation limit of region n

R_bar_n_plus — encrypted upward ramp-rate limit of region n

R_bar_n_minus — encrypted downward ramp-rate limit of region n

phi_n_plus — positive definite diagonal encryption matrix for upper capacity constraints

phi_n_minus — positive definite diagonal encryption matrix for lower capacity constraints

zeta_n_t_plus — encryption matrix for upward ramp-rate constraints at time t

zeta_n_t_minus — encryption matrix for downward ramp-rate constraints at time t

W_Q_n — private encryption matrix for distributed linear equation solving

W_P_n — private encryption matrix for distributed linear equation solving

B_Q_n — inverse DLPF submatrix related to reactive-power equations

B_P_n — inverse DLPF submatrix related to active-power equations

B_bar_Q_n — encrypted B_Q_n matrix

B_bar_P_n — encrypted B_P_n matrix

y_n_0 — initial value of ISO n in the AAC or PP-AAC algorithm

delta_n_k — random noise generated by ISO n at iteration k

pi_n_k — noise-difference term in the PP-AAC algorithm

Na — number of regions

Hn — number of decision variables in region n

H — total number of global decision variables

Nq — number of quadratic terms

Nl — number of linear terms

YALMIP — MATLAB-based optimization modeling tool

Gurobi — optimization solver

NumericFocus — Gurobi numerical robustness setting

## hasMathematicalProblemType

QP

ConvexQuadraticProgramming

ChanceConstrainedProgramming

StochasticOptimization

DistributedOptimization

PrivacyPreservingOptimization

TransformationBasedEncryptedOptimization

LinearizedOPF

## hasModeledEnergySector

Electricity

Wind
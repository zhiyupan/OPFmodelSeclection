# Reserve Constrained AC Optimal Power Flow Using Accelerated Primal-Dual Interior Point Method

## hasModelName

Reserve-Constrained AC Optimal Power Flow with Accelerated Primal-Dual Interior Point Method

## hasPaperTitle

Reserve Constrained AC Optimal Power Flow Using Accelerated Primal-Dual Interior Point Method

## hasPublicationYear

2025 online publication / 2026 journal issue

## hasDOI

10.1109/TPWRS.2025.3626450

## hasAuthor

Yehong Peng

Yong Fu

## hasInstitution

Department of Electrical and Computer Engineering, Mississippi State University, Starkville, MS, USA

# 2. MotivationAndSolvedProblem

## hasPrimaryPurpose

The model is mainly used to co-optimize energy dispatch and operating reserve allocation under a full AC optimal power flow framework, so that the system can obtain optimal power generation, secure power delivery, and reserve scheduling at the same time.

## hasMotivation

The motivation is that modern power systems are becoming more stochastic and dynamic, so they need operating reserves to maintain the balance between supply and demand under fluctuations, contingencies, and unforeseen disruptions. Existing industrial practices often optimize energy and reserves sequentially or use simplified economic dispatch models, which may neglect AC network constraints, voltage constraints, reactive power, transmission flow limits, and reserve coupling. This can lead to voltage insecurity, frequency instability, power imbalance, line congestion, and economic suboptimality. Therefore, the paper proposes a full AC network based reserve-constrained OPF and a faster customized solution method.

## hasSolvedProblem

The model solves the problem of how to efficiently incorporate a comprehensive reserve model into ACOPF, including real power reserves, reactive power reserves, device-level reserve capability limits, joint energy-reserve constraints, and zonal reserve requirements, while still keeping the large-scale nonlinear optimization problem computationally solvable.

## hasResearchQuestion

Can a reserve-constrained ACOPF model co-optimize energy and reserves under full AC network constraints, and can an accelerated primal-dual interior point method solve this large-scale nonlinear problem faster and more reliably than generic nonlinear solvers such as IPOPT?

## hasPrimaryOutput

The primary outputs are optimal real and reactive power dispatch, device reserve allocations, zonal reserve shortfalls, bus voltage magnitudes and angles, AC branch real and reactive power flows, transformer tap ratios, phase shifting angles, shunt steps, bus power imbalance penalties, branch overload penalties, reserve shortfall penalties, and total market surplus.

# 3. ModelFeature

## hasModelFeature

Reserve-Constrained OPF

Reserve-Constrained ACOPF

Energy and Reserve Co-Optimization

Full AC Network Reserve Scheduling

Single-Period RCOPF

Large-Scale RCOPF

A-PDIPM-Based OPF

Market-Surplus-Based OPF

## hasPowerFlowFormulationFeature

ACOPF

ReserveConstrainedACOPF

NonlinearACOPF

FullACNetworkModel

## hasTimeHorizonFeature

StaticOPF

SinglePeriodOPF

SinglePeriodRCOPF

## hasTemporalResolution

Not explicitly specified

Single operating period / one dispatch snapshot

## hasOptimizationHorizon

Single period

One operating snapshot

## hasUncertaintyHandlingFeature

DeterministicOPF

ReserveConstrainedOPF

NotStochasticOPF

NotRobustOPF

NotChanceConstrainedOPF

NotScenarioBasedOPF

## hasPowerSystemDomainFeature

TransmissionNetworkOPF

BulkPowerSystemOPF

PowerMarketOperationOPF

ReserveSchedulingOPF

EnergyAndAncillaryServiceCoOptimization

LargeScalePowerSystemOPF

## hasSolutionMethodEnhancementFeature

AcceleratedPrimalDualInteriorPointMethod

PDIPMBasedMethod

DirectOptimizationMethod

SymmetricJacobianMatrix

PivotingCholeskyFactorization

SparseMatrixReorderingAndScaling

NonIterativeNewtonStepSizeUpdate

PrimalDualVariableInitialization

InequalityConstraintEfficientHandling

ModelComplexityReduction

## hasModelPerformanceFeature

FastComputation

HighAccuracy

ScalableForLargeSystem

RealTimeSuitable

StableConvergence

MemoryEfficient

LargeScaleSuitable

## hasDemandSideFeature

FixedLoad

FlexibleLoad

# 4. ModelStructure

## hasObjectiveFunction

MarketSurplusMaximization

EnergyReserveCoOptimization

GenerationCostMinimization

ReserveCostMinimization

PowerImbalancePenaltyMinimization

BranchOverloadPenaltyMinimization

ReserveShortfallPenaltyMinimization

OperationalEfficiencyMaximization

## hasConstraintFunction

DevicePowerOfferBidBlockConstraint

DeviceCostBenefitDefinitionConstraint

RegulationUpReserveLimitConstraint

RegulationDownReserveLimitConstraint

SynchronizedReserveLimitConstraint

NonsynchronizedReserveLimitConstraint

RampingUpReserveLimitConstraint

RampingDownReserveLimitConstraint

ReactivePowerUpReserveLimitConstraint

ReactivePowerDownReserveLimitConstraint

OnlineReserveAvailabilityConstraint

OfflineReserveAvailabilityConstraint

ProducingDeviceEnergyReserveHeadroomConstraint

ConsumingDeviceEnergyReserveHeadroomConstraint

RealPowerUpperHeadroomConstraint

RealPowerLowerHeadroomConstraint

ReactivePowerUpDownHeadroomConstraint

ACBranchActivePowerFlowConstraint

ACBranchReactivePowerFlowConstraint

VoltageMagnitudeLimitConstraint

VoltageAngleVariableConstraint

TransformerTapRatioLimitConstraint

PhaseShiftingAngleLimitConstraint

ACBranchApparentPowerLimitConstraint

ACBranchOverloadPenaltyConstraint

ACActivePowerBalanceConstraint

ACReactivePowerBalanceConstraint

ShuntStepLimitConstraint

ZonalRegulationUpReserveRequirementConstraint

ZonalRegulationDownReserveRequirementConstraint

ZonalSynchronizedReserveRequirementConstraint

ZonalNonsynchronizedReserveRequirementConstraint

ZonalRampingUpReserveRequirementConstraint

ZonalRampingDownReserveRequirementConstraint

ZonalReactivePowerUpReserveRequirementConstraint

ZonalReactivePowerDownReserveRequirementConstraint

ZonalReserveShortfallConstraint

LinearInequalityFeasibilityConstraint

NonlinearBranchFlowInequalityTransformedEqualityConstraint

BarrierFunctionInequalityHandling

PerturbedKKTCondition

PrimalDualFeasibilityCondition

## usesParameter

D

G

I

L

M

Np

Nq

Sh

i

j

l

m

n

gij

bij

gij_sh

bij_sh

sl_max

v_min

v_max

tau_min

tau_max

phi_min

phi_max

theta

vi

tauij

phiij

Delta_gsh

Delta_bsh

pj_max

pj_min

qj_max

qj_min

pij

qij

pj

qj

pjm

p_jm_max

u_hat_on

u_hat_off

p_rgu

p_rgd

p_scr

p_nsc

p_rru_on

p_rru_off

p_rrd_on

p_rrd_off

q_qru

q_qrd

p_sup_max

p_sup_req

q_sup_req

sigma_sup

p_rgu_req

p_rgd_req

p_scr_req

p_nsc_req

p_rru_req

p_rrd_req

q_qru_req

q_qrd_req

reserve shortfall variables

cp

cq

cs

c_jm

c_sup_j

c_sup_n

zj

zp_i

zq_i

zs_l

zsup_j

zsup_n

x

F(x)

H(x)

G(x)

Ag

S

t

u

v

KKT residual

Newton direction

alpha

sigma_alpha

epsilon_cvg

k_max

Jacobian matrix

symmetric coefficient matrix

pivoting Cholesky factorization

## hasSolutionDetailsSummary

The paper formulates a single-period reserve-constrained ACOPF problem and solves it using a customized accelerated primal-dual interior point method. The RCOPF is written as a nonlinear optimization problem with equality constraints and inequality constraints. Unlike common PDIPM implementations that introduce slack variables for all inequality constraints, the proposed A-PDIPM only introduces slack variables for nonlinear AC branch apparent flow constraints, while directly handling the large number of linear inequality constraints through barrier functions and feasibility-preserving step-size updates. The method applies Newton’s method to perturbed KKT conditions, constructs a fully symmetric Jacobian matrix, uses pivoting Cholesky factorization to solve sparse linear systems, reuses symbolic matrix analysis across iterations, applies direct non-iterative Newton step-size updates, and uses problem-specific primal-dual variable initialization.

## hasModelValidationSummary

The model and algorithm are validated using datasets from the US DOE ARPA-E Grid Optimization Competition Challenge 3. Test systems range from a small 73-bus case to a large-scale 23,643-bus case. The paper first compares RCOPF with Pre-Reserve OPF and Post-Reserve OPF to show the economic benefits of energy-reserve co-optimization. It then evaluates the heuristic corrective mechanism, the proposed primal-dual initialization strategy, and the performance of A-PDIPM against IPOPT, both with and without reserve constraints. The authors also report selected results from 30 networks/scenarios and state that the method was successfully tested on more than 1000 datasets.

## hasFindingsSummary

The case studies show that RCOPF can outperform sequential or simplified reserve allocation methods by achieving higher total market surplus and avoiding power flow non-convergence, branch overload, and reserve shortfall problems. The proposed A-PDIPM is faster and more stable than IPOPT, especially for large-scale systems and cases with reserve constraints. Without reserve constraints, A-PDIPM reduces CPU time by up to 87.05% in the 23,643-bus case. With reserve constraints, it achieves time savings from 36.36% to 88.81% and can solve large cases where IPOPT fails to converge. Across selected test cases, the method obtains converged and secure power flow solutions with very small bus imbalance penalties and no line flow violations.

## hasStrengthsAndLimitationsSummary

The main strength of the model is that it co-optimizes energy and reserves under a full nonlinear AC network model, instead of using simplified economic dispatch or DC approximations. It includes detailed real and reactive reserve categories, device-level reserve capability constraints, energy-reserve joint constraints, zonal reserve requirements, and reserve shortfall penalties. The proposed A-PDIPM is customized for RCOPF and improves speed, memory efficiency, and convergence stability for large-scale cases. However, the model in this paper is single-period rather than multi-period. Device on/off statuses are assumed to be given, so unit commitment is not directly optimized inside this RCOPF module. Transformer tap ratios, phase-shifting angles, and shunt steps are treated as continuous variables. The paper also does not solve the full original GO3 problem with unit commitment, N-k contingency analysis, and multi-period coordination in one integrated model; instead, it focuses on the key single-period RCOPF submodule. Future work is needed for real-time look-ahead, day-ahead, weekly-ahead, uncertainty analysis, and multi-period operation.

## isScenarioSuitability

True / scenario-applicable

## MonteCarlo

False

## hasFurtherProperty

1. The paper focuses on single-period RCOPF, not full unit commitment.
2. Device on/off statuses are assumed to be given.
3. The original ARPA-E GO3 problem includes security-constrained ACOPF with unit commitment and reserve allocation, but this paper focuses on the RCOPF submodule.
4. The reserve model includes regulation up/down reserves, synchronized and nonsynchronized reserves, ramping up/down reserves, and reactive power up/down reserves.
5. The A-PDIPM method is a customized direct nonlinear programming method rather than a convex relaxation or decomposition method.
6. The model is highly relevant for energy and ancillary service co-optimization.

# Objective Property

## hasMathematicalProblemType

NLP

NonlinearProgramming

NonconvexOptimization

InteriorPointMethodBasedOptimization

PrimalDualInteriorPointMethod

LargeScaleSparseNonlinearOptimization

## hasModeledEnergySector

Electricity
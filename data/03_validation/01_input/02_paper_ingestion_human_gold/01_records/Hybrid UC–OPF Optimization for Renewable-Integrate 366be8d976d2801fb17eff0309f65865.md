# Hybrid UC–OPF Optimization for Renewable-Integrated Power Systems

## hasModelName

Hybrid MINLP–PSO–NR UC–OPF Model for Renewable-Integrated Power Systems

## hasPaperTitle

Hybrid UC–OPF Optimization for Renewable-Integrated Power Systems

## hasPublicationYear

2025

## hasDOI

10.1109/COSITE68330.2025.11414305

## hasAuthor

Muhammad Nurul Hadi

Ramdhan Halid Siregar

Rakhmad Syafutra Lubis

## hasInstitution

Department of Electrical and Computer Engineering, Universitas Syiah Kuala, Banda Aceh, Indonesia

---

# 2. MotivationAndSolvedProblem

## hasPrimaryPurpose

To obtain a 24-hour unit commitment and generation dispatch schedule for a renewable-integrated power system, and then check and improve the technical feasibility of that schedule through Newton–Raphson power flow analysis and PSO-based OPF refinement.

## hasMotivation

PV generation is intermittent and time-varying, which can disturb power balance, increase thermal generator cycling, increase start-up costs, and create power-flow feasibility problems. Existing UC or renewable-integration studies often do not jointly handle renewable generation, unit commitment scheduling, and power-flow feasibility in one workflow.

## hasSolvedProblem

The model addresses the problem of producing an economically efficient UC schedule that is also technically feasible with respect to AC power-flow constraints, voltage limits, line capacity limits, generator limits, PHS operation, and ramping-related violations.

## hasResearchQuestion

Can a hybrid MINLP–PSO–NR UC–OPF framework produce a low-cost 24-hour generation schedule for a PV- and PHS-integrated power system while reducing power-flow constraint violations?

## hasPrimaryOutput

24-hour unit commitment schedule

Hourly generator dispatch

PV output contribution

PHS operation profile

Power-flow feasibility results

Voltage and line-flow feasibility status

Penalty values for constraint violations

Operational cost

Fitness value after OPF refinement

---

# 3. ModelFeature

## hasModelFeature

Hybrid UC–OPF

Renewable-Integrated UC–OPF

MINLP-Based Unit Commitment

PSO-Based OPF Refinement

Newton–Raphson Power Flow Feasibility Check

Penalty-Based Feasibility Correction

## hasPowerFlowFormulationFeature

ACOPF

NonlinearACPowerFlow

NewtonRaphsonPowerFlow

## hasTimeHorizonFeature

MultiPeriodOPF

DayAheadScheduling

TimeCoupledUnitCommitment

## hasTemporalResolution

1 h

## hasOptimizationHorizon

24 h

## hasUncertaintyHandlingFeature

DeterministicOPF

TimeVaryingPVProfile

## hasPowerSystemDomainFeature

TransmissionNetworkOPF

RenewableIntegratedPowerSystem

PVIntegratedPowerSystem

PumpedHydroStorageIntegratedPowerSystem

ModifiedIEEE30BusSystem

## hasSolutionMethodEnhancementFeature

HybridOptimization

MINLPBasedOptimization

PSOBasedMetaheuristicOptimization

NewtonRaphsonFeasibilityCheck

PenaltyFunctionMethod

SelectiveViolationHourRefinement

## hasModelPerformanceFeature

PowerFlowFeasibilityImprovement

ConstraintViolationReduction

EconomicFeasibilityTradeoff

ComputationalEfficiencyOriented

TechnicallyFeasibleDispatch

## hasDemandSideFeature

FixedLoad

---

# 4. ModelStructure

## hasObjectiveFunction

CostMinimization

ConstraintViolationPenaltyMinimization

## hasConstraintFunction

PowerLoadBalanceConstraint

GeneratorActivePowerLimitConstraint

GeneratorReactivePowerLimitConstraint

MinimumUpTimeConstraint

MinimumDownTimeConstraint

RampingRateConstraint

PHSStorageCapacityConstraint

PHSEnergyBalanceConstraint

ACActivePowerBalanceConstraint

ACReactivePowerBalanceConstraint

BusVoltageMagnitudeLimitConstraint

LineCapacityLimitConstraint

NewtonRaphsonConvergencePenaltyConstraint

## usesParameter

NT — number of operating periods

NG — number of thermal generators

NPV — number of PV units

NPHS — number of PHS units

t — time index

PLD(t) — load demand at time t

PGT_i(t) — thermal generator active power output

PPV_i(t) — PV active power output

PPHS_output_i(t) — PHS discharge or output power

PPHS_input_i(t) — PHS pumping or input power

QG_i — generator reactive power output

u_i,t — generator on/off commitment status

PGT_i_min — minimum active power output of generator i

PGT_i_max — maximum active power output of generator i

QG_i_min — minimum reactive power output of generator i

QG_i_max — maximum reactive power output of generator i

MUT_i — minimum up-time of generator i

MDT_i — minimum down-time of generator i

ramp rate — generator ramping limit

a_i — quadratic fuel-cost coefficient

b_i — linear fuel-cost coefficient

c_i — constant fuel-cost coefficient

FC_i — thermal generator fuel-cost function

SUC — start-up cost

SDC — shut-down cost

CPHS — PHS operational cost

PHS efficiency — efficiency of pumped hydro storage

PHS initial storage level — initial stored energy level

PHS minimum capacity — lower bound of PHS storage level

PHS maximum output power — maximum PHS discharge power

V_k — voltage magnitude at bus k

delta_k — voltage angle at bus k

G_kn — conductance term between bus k and bus n

B_kn — susceptance term between bus k and bus n

S_kn — line power flow or line capacity between bus k and bus n

line impedance — transmission line impedance

network topology — bus and branch connection structure

pV — voltage deviation penalty weight

pP — active power violation penalty weight

pQ — reactive power violation penalty weight

pLine — line capacity violation penalty weight

pRamp — ramping violation penalty weight

pNR — Newton–Raphson non-convergence penalty weight

## hasSolutionDetailsSummary

The paper uses a two-stage hybrid UC–OPF procedure. First, a 24-hour Unit Commitment problem is solved using MINLP through the SCIP solver and PySCIPOpt. The resulting UC dispatch is then checked by Newton–Raphson AC power flow. If the UC dispatch satisfies the power-flow constraints, the solution is accepted. If violations occur, the model identifies the violated hours and applies PSO-based OPF refinement only to those hours. The PSO fitness function combines generation cost with penalty terms for voltage deviation, active power violation, reactive power violation, transmission line capacity violation, ramping violation, and Newton–Raphson convergence failure.

## hasModelValidationSummary

The model is validated on a modified IEEE 30-bus system with thermal generators, PV units, and Pumped Hydro Storage. The test setup includes generator cost coefficients, generator active and reactive power limits, voltage limits, PHS capacity and efficiency data, PHS O&M cost, 24-hour load data, and 24-hour PV output data. The paper compares three stages: UC Optimization Only, After Power Flow Analysis, and After OPF Optimization.

## hasFindingsSummary

The MINLP-based UC stage gives the lowest operational cost, 8876.92 USD, but the resulting dispatch violates several power-flow constraints. After Newton–Raphson power-flow analysis, the operational cost increases to 9029.514 USD and the penalty reaches 302210.9. After PSO–NR OPF refinement, the penalty decreases to 2128.49, while operational cost increases to 9280.94 USD. The final result shows a trade-off: slightly higher cost but much better technical feasibility.

## hasStrengthsAndLimitationsSummary

The main strength is that the model combines UC scheduling, renewable integration, AC power-flow feasibility checking, and PSO-based OPF correction in one workflow. It can produce a low-cost UC schedule and then reduce technical violations through NR-based feasibility checking and PSO refinement. The main limitation is that the model is deterministic: PV output is treated as a given time-varying profile rather than as a stochastic variable. The validation is limited to a modified IEEE 30-bus system. The method also relies on PSO only after violations are detected, so it is a repair-oriented OPF refinement rather than a fully integrated large-scale UC–ACOPF formulation.

## isScenarioSuitability

Partially suitable

## MonteCarlo

False

## hasFurtherProperty

The model is better described as a hybrid UC–OPF scheduling and feasibility-refinement framework, not as a conventional single-stage OPF model.

PV output is treated as a deterministic time-varying input profile.

PHS is modeled as a balancing or backup resource and shows relatively low utilization in the reported results.

There is a possible inconsistency in the paper regarding PV/PHS bus placement: the text states that PV is placed at bus 6 and PHS at bus 25, while Table II lists PV at bus 25.

---

# Objective Property

## hasObjectiveFunction

CostMinimization

ThermalGenerationCostMinimization

StartupShutdownCostMinimization

PHSOperationCostMinimization

ConstraintViolationPenaltyMinimization

## hasConstraintFunction

PowerLoadBalanceConstraint

GeneratorActivePowerLimitConstraint

GeneratorReactivePowerLimitConstraint

MinimumUpTimeConstraint

MinimumDownTimeConstraint

RampingRateConstraint

PHSStorageCapacityConstraint

PHSEnergyBalanceConstraint

ACActivePowerBalanceConstraint

ACReactivePowerBalanceConstraint

BusVoltageMagnitudeLimitConstraint

LineCapacityLimitConstraint

NewtonRaphsonConvergencePenaltyConstraint

## usesParameter

ThermalGeneratorCostCoefficient

ThermalGeneratorActivePowerLimit

ThermalGeneratorReactivePowerLimit

GeneratorCommitmentStatus

GeneratorMinimumUpDownTime

GeneratorRampRate

PVOutputProfile

LoadDemandProfile

PHSStorageCapacity

PHSChargeDischargePower

PHSEfficiency

BusVoltageMagnitude

BusVoltageAngle

NetworkAdmittanceParameter

LineCapacityLimit

PenaltyWeightParameter

OptimizationTimeIndex

## hasMathematicalProblemType

MINLP

NLP

NonconvexOptimization

MetaheuristicOptimization

PenaltyBasedOptimization

## hasModeledEnergySector

Electricity

PV

PumpedHydroStorage

Hydro, inferred from Pumped Hydro Storage
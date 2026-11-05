# Multi-Period Hybrid AC/DC-OPF Model for Flexibility Market Clearing With Seamless TSO-DSO Coordination

## hasModelName

Multi-Period Hybrid AC/DC-OPF Model for Flexibility Market Clearing with Seamless TSO-DSO Coordination

## hasPaperTitle

Multi-Period Hybrid AC/DC-OPF Model for Flexibility Market Clearing With Seamless TSO-DSO Coordination

## hasPublicationYear

2023

## hasDOI

10.1109/ACCESS.2023.3269423

## hasAuthor

Damian Sieraszewski

Ole Kjærland Olsen

Dmytro Ivanko

Irina Oleinikova

Hossein Farahmand

## hasInstitution

Department of Electric Power Engineering, Norwegian University of Science and Technology, Trondheim, Norway

NORCE Norwegian Research Centre, Stavanger, Norway

# 2. MotivationAndSolvedProblem

## hasPrimaryPurpose

The model is mainly used to clear a local flexibility market and coordinate transmission and distribution system operation by jointly optimizing flexibility activation, distribution-grid operation, and transmission-grid operation over multiple time periods.

## hasMotivation

The motivation is that increasing electrification, distributed energy resources, electric vehicles, and electric heating create new congestion, voltage-control, balancing, and grid-security challenges. Consumer-side flexibility assets can help solve these problems, but this requires a market-clearing and coordination model that can represent both distribution-grid constraints and transmission-grid constraints.

## hasSolvedProblem

The model solves the problem of how to activate distributed flexibility resources in a local flexibility market while respecting both DSO-side distribution-grid constraints and TSO-side transmission-grid constraints.

## hasResearchQuestion

Can a multi-period hybrid AC/DC-OPF model, combining SOC-ACOPF for the distribution grid and DC-OPF for the transmission grid, support flexibility market clearing and seamless TSO-DSO coordination?

## hasPrimaryOutput

The primary outputs are optimal flexibility activation, flexible generation dispatch, flexible load shifting, load shedding, battery charging and discharging, battery state of charge, AC-side active and reactive generation, DC-side generation, DC line flows, voltage angles, distribution-grid voltage profiles, power exchanged at the TSO-DSO interface, and total operating cost.

# 3. ModelFeature

## hasModelFeature

Hybrid AC/DC-OPF

Multi-Period OPF

Flexibility Market Clearing OPF

TSO-DSO Coordination OPF

Distributed Flexibility Resource Optimization

Local Flexibility Market Model

Transmission-Distribution Coordinated OPF

## hasPowerFlowFormulationFeature

HybridACDCOPF

SOCACOPF

DCOPF

ConvexRelaxedACOPF

SOCPRelaxation

TransmissionDistributionCoupledOPF

## hasTimeHorizonFeature

MultiPeriodOPF

DayAheadOPF

RollingHorizonOPF

OperationalFlexibilityScheduling

IntradayBalancingFlexibilityMarketOPF

## hasTemporalResolution

1 h for day-ahead market

15 min for local flexibility market operation

## hasOptimizationHorizon

24 h

1 day

Day-ahead operation horizon

Quarter-hour operation intervals within the day

## hasUncertaintyHandlingFeature

DeterministicOPF

ScenarioCapableOPF

NotFullStochasticOPF

NotMonteCarloOPF

## hasPowerSystemDomainFeature

TransmissionNetworkOPF

DistributionNetworkOPF

ActiveDistributionNetworkOPF

TSODSOCoordination

LocalFlexibilityMarket

DistributedEnergyResourceOPF

DistributedFlexibilityAssetOPF

## hasSolutionMethodEnhancementFeature

ConvexRelaxation

SOCPRelaxation

HybridACDCFormulation

MultiPeriodOptimization

MarketClearingOptimization

PyomoBasedOptimization

GurobiSolver

TransmissionDistributionConnectionConstraint

## hasModelPerformanceFeature

HighAccuracy

ComputationalEfficiency

FastAndStableConvexRelaxation

TransmissionDistributionCoordination

FlexibilityActivationSupport

VoltageProblemMitigation

CongestionManagement

## hasDemandSideFeature

FlexibleLoad

DemandResponse

ShiftableLoad

LoadShedding

FixedLoad

# 4. ModelStructure

## hasObjectiveFunction

ProductionCostMinimization

FlexibilityProcurementCostMinimization

OperationalCostMinimization

BatteryOperationCostMinimization

LoadSheddingCostMinimization

MarketClearingCostMinimization

GridConstraintFeasibleCostMinimization

## hasConstraintFunction

ACActivePowerBalanceConstraint

ACReactivePowerBalanceConstraint

SOCRelaxationConstraint

AuxiliaryVariableConstraint

ACGenerationLimitConstraint

ACReactiveGenerationLimitConstraint

DCPowerBalanceConstraint

DCLineFlowConstraint

DCLineCapacityConstraint

DCGenerationLimitConstraint

SlackAngleConstraint

ACDCConnectionConstraint

TSODSOInterfaceConstraint

FlexibleGenerationLimitConstraint

FlexibleLoadLimitConstraint

LoadShiftingEnergyNeutralityConstraint

LoadSheddingConstraint

BatteryStateOfChargeConstraint

BatteryChargingLimitConstraint

BatteryDischargingLimitConstraint

BatteryNoSimultaneousChargeDischargeConstraint

BatteryStateTransitionConstraint

TerminalStateOfChargeConstraint

VoltageRegulationConstraint

CongestionManagementConstraint

TransmissionLineCapacityConstraint

DistributionLineOperationalFeasibilityConstraint

## usesParameter

N

n

M

m

T

t

U

u

j

B_nj

G_mj

B_mj

P_L_AC

Q_L_AC

P_L_DC

P_fl_max

theta_slack

P_G_AC_max

P_G_AC_min

Q_G_AC_max

Q_G_AC_min

P_G_DC_max

P_G_DC_min

P_G_Flex_max

P_G_Flex_min

P_L_Flex_max

P_L_Flex_min

P_SoC_init

P_SoC_max

P_SoC_min

P_ch_max

P_disch_max

eta_ch

eta_disch

c_G

c_Flex

c_Batt

c_LS

day-ahead price

DFR price factor

Nord Pool price data

u_m

R_mj

I_mj

P_G_AC

Q_G_AC

P_G_DC

P_fl

theta

P_G_Flex

P_L_Flex

P_LS

P_SoC

P_ch

P_disch

delta

load profile

price profile

DFR availability

line capacity

voltage magnitude

TSO-DSO interface power

## hasSolutionDetailsSummary

The paper develops a multi-period hybrid AC/DC-OPF model. The distribution grid is represented by SOC-ACOPF, also called Jabr’s model, while the transmission grid is represented by DC-OPF. These two OPF formulations are coupled through an AC-to-DC connection constraint, where the distribution feeder node is seen as a load from the transmission-grid perspective. The model is then extended to include flexible generation, flexible load, load shedding, and battery storage across hourly and quarter-hour time steps. The implementation is done in Python using Pyomo as the optimization modeling language and Gurobi as the solver.

## hasModelValidationSummary

The model is validated as a proof of concept using a 33-node radial distribution grid and a 9-node meshed transmission grid. The distribution and transmission grids are connected by merging one transmission node and one distribution feeder node. The test setup includes distributed flexibility resources such as load shifting, distributed generation, and batteries. Price and load data are derived from Nord Pool market data. The paper compares the hybrid AC/DC-OPF model with standalone DC-OPF and standalone SOC-ACOPF models, and then tests the model in several cases: flexibility optimization in the distribution grid, voltage-problem mitigation, distribution-grid congestion management, and transmission-grid congestion management.

## hasFindingsSummary

The model shows that using distributed flexibility resources can reduce operating costs, improve voltage profiles, reduce imported active power from the transmission grid, reduce active power losses in the distribution grid, avoid or reduce load shedding, and help relieve both distribution-grid and transmission-grid congestion. In one distribution-grid flexibility case, imported active power from the transmission grid decreases by 40 percent and active power losses decrease by 7.5 percent. In voltage and congestion cases, flexible load and battery dispatch are preferred because of their lower prices, while distributed generation is used more significantly when voltage or congestion problems require it. The model also demonstrates that distribution-side flexibility can support the transmission grid by creating reverse power flow at the TSO-DSO interface.

## hasStrengthsAndLimitationsSummary

The main strength of the model is that it combines transmission-grid and distribution-grid OPF into one optimization problem and explicitly represents flexibility market clearing with distributed flexibility assets. The SOC-ACOPF formulation gives better accuracy for active distribution grids than DC-OPF, while DC-OPF keeps the transmission-grid model computationally simple. The model can handle multi-period operation and solve voltage and congestion problems through flexibility activation. However, the paper mainly presents a proof of concept rather than a real-life large-scale implementation. The scenario-generation part is mentioned but not fully developed. The price and load data include simplifications. The authors also note that if one TSO coordinates with several DSOs in a single optimization problem, computational complexity will increase significantly, so future work extends the model with ADMM.

## isScenarioSuitability

Partially true / scenario-capable

## MonteCarlo

False

## hasFurtherProperty

1. The model is not a pure ACOPF, pure DCOPF, or pure distribution OPF model. It is a hybrid transmission-distribution OPF model.
2. The distribution grid is modeled with SOC-ACOPF because active distribution grids have high R/X ratios and DC-OPF is not accurate enough for them.
3. The transmission grid is modeled with DC-OPF to reduce computational burden.
4. The model contains battery binary operation variables, so the multi-period flexibility extension may be treated as a mixed-integer conic optimization problem.
5. ADMM is not part of the model in this paper; it is mentioned as future work for coordinating one TSO with multiple DSOs.

# Objective Property

## hasMathematicalProblemType

SOCP

ConvexOptimization

LinearProgrammingComponent

DCOPF

SOCACOPF

HybridACDCOPF

MultiPeriodOptimization

MISOCP

## hasModeledEnergySector

Electricity
# Machine Learning-Aided Security Constrained Optimal Power Flow

## hasModelName

Machine Learning-Aided Security-Constrained Optimal Power Flow Model

## hasPaperTitle

Machine Learning-Aided Security Constrained Optimal Power Flow

## hasPublicationYear

2020

## hasDOI

Not explicitly provided in the uploaded paper text

## hasAuthor

Jubeyer Rahman

Cong Feng

Jie Zhang

## hasInstitution

The University of Texas at Dallas, Richardson, TX, USA

# 2. MotivationAndSolvedProblem

## hasPrimaryPurpose

The model is mainly used to solve security-constrained AC optimal power flow faster by combining supervised machine learning with physical network equations. The machine learning model predicts bus voltage magnitudes and voltage angles, and then network equations are used to calculate the remaining OPF variables.

## hasMotivation

The motivation is that full AC OPF is highly nonlinear and nonconvex, making it difficult and time-consuming to solve, especially for large-scale networks. In deregulated electricity markets, system operators need frequent and accurate OPF solutions to produce dispatch decisions and market signals, especially under renewable uncertainty. Pure machine-learning OPF methods can be fast, but they often violate equality constraints and physical network constraints. Hybrid methods using physical solvers are feasible but still limited in speed because they depend on conventional OPF solvers.

## hasSolvedProblem

The model solves the problem of how to improve OPF computational speed while avoiding the constraint violations that commonly occur in end-to-end machine-learning OPF methods. Instead of predicting real power generation directly, it predicts voltage magnitudes and angles, then uses physics-based equations to compute current injection, complex power injection, generator output, shunt variables, branch flow, and generation cost.

## hasResearchQuestion

Can a machine learning-aided SCOPF method predict voltage magnitudes and angles using a random forest model and then use physical network equations to obtain near-optimal, constraint-satisfying OPF solutions faster than conventional MATPOWER MIPS?

## hasPrimaryOutput

The primary outputs are predicted bus voltage magnitudes, predicted bus voltage angles, calculated current injections, complex power injections, generator active and reactive power outputs, switched shunt susceptance values, branch power flows, and generation cost.

# 3. ModelFeature

## hasModelFeature

MachineLearningAidedOPF

SecurityConstrainedOPF

RandomForestBasedOPF

PhysicsInformedMachineLearningOPF

SupervisedLearningOPF

FastOPFProxy

VoltagePredictionBasedOPF

MLAidedACOPF

## hasPowerFlowFormulationFeature

ACOPF

SecurityConstrainedACOPF

PhysicsBasedNetworkEquationOPF

FullACNetworkEquationPostCalculation

## hasTimeHorizonFeature

StaticOPF

SinglePeriodOPF

SnapshotBasedOPF

FastRepeatedOPFSolving

## hasTemporalResolution

1 h load samples for dataset generation

No explicit OPF time-step coupling

## hasOptimizationHorizon

Single operating snapshot

## hasUncertaintyHandlingFeature

DeterministicOPF

DataDrivenScenarioEvaluation

LoadProfileSampleBasedTesting

NotStochasticOPF

NotRobustOPF

NotChanceConstrainedOPF

NotMonteCarloOPF

## hasPowerSystemDomainFeature

TransmissionNetworkOPF

LargeScaleNetworkOPF

SecurityConstrainedPowerSystemOperation

ElectricityMarketDispatchOPF

500BusTransmissionNetwork

## hasSolutionMethodEnhancementFeature

LearningAssistedOPF

RandomForestRegression

MultiInputMultiOutputRegression

PhysicsBasedPostProcessing

NetworkEquationBasedRecovery

ScikitLearnRandomForestRegressor

MATPOWERGeneratedTrainingData

MIPSBaselineComparison

## hasModelPerformanceFeature

FastComputation

RealTimeSuitable

ConstraintViolationReduction

NearOptimalSolution

HighComputationalEfficiency

SolverFreePredictionAfterTraining

## hasDemandSideFeature

FixedLoad

# 4. ModelStructure

## hasObjectiveFunction

GenerationCostMinimization

OperationalCostMinimization

PiecewiseLinearGenerationCostMinimization

NearOptimalCostPrediction

## hasConstraintFunction

BusVoltageMagnitudeLimitConstraint

BusVoltageAngleLimitConstraint

GeneratorActivePowerLimitConstraint

GeneratorReactivePowerLimitConstraint

SwitchedShuntSusceptanceLimitConstraint

ACActivePowerBalanceConstraint

ACReactivePowerBalanceConstraint

BranchApparentPowerFlowLimitConstraint

SecurityRelatedSwitchedShuntConstraint

VoltageMagnitudePrediction

VoltageAnglePrediction

SlackBusAngleReferenceHandling

CurrentInjectionCalculationUsingBusAdmittanceMatrix

ComplexPowerInjectionCalculation

GeneratorBusPowerInjectionRecovery

BranchFlowRecoveryFromPredictedVoltageParameters

## usesParameter

N

E

B

G

Pd

Qd

pg

qg

cg

piecewise linear cost coefficients

v

theta

vi_min

vi_max

theta_i_min

theta_i_max

Y

I_inj

S

S_inj

S_d

p_i_j

q_i_j

sf

b_cs

b_cs_min

b_cs_max

branch rating

line parameters

transformer parameters

X_train

Y_train

X_test

Y_test

number of trees

maximum tree depth

minimum samples split

out-of-bag error

residual sum of squares

RandomForestRegressor

GridSearch

training dataset

testing dataset

## hasSolutionDetailsSummary

The paper proposes a machine learning-aided SCOPF solution method. First, MATPOWER MIPS is used offline to generate OPF solutions for training. The input features are real and reactive loads, and the supervised learning outputs are bus voltage magnitudes and voltage angles. A multi-input multi-output random forest regression model is trained on the generated dataset. During online solving, given a new load condition, the random forest predicts voltage magnitude and angle. Then physics-based network equations are used to calculate current injection using the bus admittance matrix, compute apparent and complex power injections, recover generator outputs and shunt variables, calculate generation cost, and check branch flow constraints. This avoids directly predicting all OPF variables and reduces equality constraint violations.

## hasModelValidationSummary

The method is validated on a 500-bus transmission network from the ARPA-E Grid Optimization competition repository. The system includes 51 active generators, 17 controllable shunts, 200 load buses, and 593 branches. To generate training samples, the base-case load is extended using the 2011 hourly load profile of the ERCOT system, producing 8,760 load samples. MATPOWER MIPS is used to solve the SCOPF cases, and only converged cases are used for training and testing. 80% of the data are used for training and 20% for testing. The proposed ML-aided method is compared with MATPOWER MIPS and with a pure end-to-end machine learning approach.

## hasFindingsSummary

The results show that the proposed machine learning-aided approach achieves zero inequality constraint violations and zero equality constraint violations in the tested cases, while the pure end-to-end machine learning approach has 100% equality constraint violations. The proposed method achieves an optimality metric of 1.123 × 10^-4 compared with MIPS. For 1,080 test cases, MATPOWER MIPS requires 2030.4 seconds in total and 1.88 seconds per case on average, while the machine learning-aided solver requires 35.26 seconds in total and 0.032 seconds per case on average. This corresponds to a 58.75 times computational speed improvement.

## hasStrengthsAndLimitationsSummary

The main strength of the model is that it combines machine learning speed with physical network equations, so it avoids many constraint violations that occur in pure end-to-end machine learning OPF. By predicting voltage magnitudes and angles instead of generator real power directly, the model preserves the physical relationship between voltages, current injection, power injection, and branch flows. It significantly reduces solution time compared with MATPOWER MIPS and is potentially useful for post-contingency analysis where many network topologies and load profiles must be evaluated quickly. However, the method depends on offline OPF solutions generated by MATPOWER, so it is not independent of conventional solvers during the training-data generation stage. The validation is limited to one 500-bus network. The method uses random forest rather than deep learning, and the authors state that future work will test larger networks and other learning techniques.

## isScenarioSuitability

True / scenario-applicable

## MonteCarlo

False

## hasFurtherProperty

1. The model is not a pure end-to-end machine learning OPF model. It is a machine learning-aided OPF model with physical network equation recovery.
2. The key design choice is to predict voltage magnitude and voltage angle instead of directly predicting generator real power output.
3. The model avoids running a physical OPF solver online after training, but it still needs MATPOWER MIPS to generate training data offline.
4. The benchmark pure ML method directly predicts v, theta, pg, qg, and bcs, but it suffers from equality constraint violations.
5. The proposed method is suitable for fast repeated OPF evaluation and post-contingency analysis.

# Objective Property

## hasMathematicalProblemType

NLP

NonconvexOptimization

ACOPF

SecurityConstrainedOPF

SupervisedLearningRegression

RandomForestRegression

LearningAssistedOptimization

## hasModeledEnergySector

Electricity
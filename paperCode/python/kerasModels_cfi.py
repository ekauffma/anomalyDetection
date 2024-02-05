import FWCore.ParameterSet.Config as cms

CICADA_v1p2p0_Ntuplizer = cms.EDAnalyzer(
    'kerasCICADAModelNtuplizer',
    regionToken = cms.untracked.InputTag("simCaloStage2Layer1Digis"),
    branchName = cms.string("CICADA_v1p2p0_score"),
    treeName = cms.string("CICADA_v1p2p0"),
    modelLocation = cms.string("/src/anomalyDetection/paperCode/data/models/data_models_30Jan2024/cicada-v1/")
)

CICADA_v2p2p0_Ntuplizer = cms.EDAnalyzer(
    'kerasCICADAModelNtuplizer',
    regionToken = cms.untracked.InputTag("simCaloStage2Layer1Digis"),
    branchName = cms.string("CICADA_v2p2p0_score"),
    treeName = cms.string("CICADA_v2p2p0"),
    modelLocation = cms.string("/src/anomalyDetection/paperCode/data/models/data_models_30Jan2024/cicada-v2/")    
)

CICADA_v1p2p0N_Ntuplizer = cms.EDAnalyzer(
    'kerasCICADAModelNtuplizer',
    regionToken = cms.untracked.InputTag("simCaloStage2Layer1Digis"),
    branchName = cms.string("CICADA_v1p2p0N_score"),
    treeName = cms.string("CICADA_v1p2p0N"),
    modelLocation = cms.string("/src/anomalyDetection/paperCode/data/models/mc_models_05Feb2024/cicada-v1/")
)

CICADA_v2p2p0N_Ntuplizer = cms.EDAnalyzer(
    'kerasCICADAModelNtuplizer',
    regionToken = cms.untracked.InputTag("simCaloStage2Layer1Digis"),
    branchName = cms.string("CICADA_v2p2p0N_score"),
    treeName = cms.string("CICADA_v2p2p0N"),
    modelLocation = cms.string("/src/anomalyDetection/paperCode/data/models/mc_models_05Feb2024/cicada-v2/")
)

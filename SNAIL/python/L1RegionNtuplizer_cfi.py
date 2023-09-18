import FWCore.ParameterSet.Config as cms

L1RegionNtuplizer = cms.EDAnalyzer(
    'L1RegionNtuplizer',
    regionToken = cms.InputTag("simCaloStage2Layer1Digis")
)
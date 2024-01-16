import FWCore.ParameterSet.Config as cms

puppiJetNtuplizer = cms.EDAnalyzer(
    'jetNtuplizer',
    objectSrc = cms.InputTag("slimmedJetsPuppi")
)

jetNtuplizer = cms.EDAnalyzer(
    'jetNtuplizer',
    objectSrc = cms.InputTag("slimmedJets")
)
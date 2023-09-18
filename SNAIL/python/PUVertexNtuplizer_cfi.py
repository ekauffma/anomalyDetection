import FWCore.ParameterSet.Config as cms

PUVertexNtuplizer = cms.EDAnalyzer(
    'PUVertexNtuplizer',
    pvSrc = cms.InputTag('offlineSlimmedPrimaryVertices'),
)
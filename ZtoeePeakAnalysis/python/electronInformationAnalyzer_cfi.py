import FWCore.ParameterSet.Config as cms

electronInformationAnalyzer = cms.EDAnalyzer(
    'electronInformationAnalyzer',
    electronSource = cms.InputTag("slimmedElectrons")
)
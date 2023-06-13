import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run2_2018_cff import Run2_2018

import FWCore.ParameterSet.VarParsing as VarParsing
options = VarParsing.VarParsing ('analysis')
options.parseArguments()

process = cms.Process("USERTEST",Run2_2018)
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.maxEvents)
)

process.MessageLogger.cerr.FwkReport.reportEvery = 20000

#attempt to get rid of muon shower warning
process.MessageLogger.suppressWarning = cms.untracked.vstring(
    'l1UpgradeTree',
    'l1UpgradeEmuTree',
    'l1UpgradeTfMuonShowerTree', 
    'emtfStage2Digis', 
    'l1uGTTestcrateTree', 
    'simDtTriggerPrimitiveDigis'
)

#Define out input source
process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring("/store/data/Run2018C/ZeroBias/MINIAOD/UL2018_MiniAODv2-v1/120000/1D803173-3B62-E349-9FD6-504C7A98BD41.root"),
                            secondaryFileNames = cms.untracked.vstring(
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/319/348/00000/C6FD98EF-0E83-E811-9BF1-02163E00AD83.root",
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/319/579/00000/C4FC8B0D-0287-E811-BB47-FA163EC44199.root",
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/319/950/00000/E0608FF1-CC8B-E811-8560-FA163E250820.root",
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/320/065/00000/68869D46-328E-E811-A6F7-FA163E9D3E3D.root",
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/320/065/00000/6ECB9486-328E-E811-849E-02163E016496.root",
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/319/993/00000/2EEA94BB-898C-E811-820F-FA163EC91118.root",
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/319/993/00000/9E0D4582-898C-E811-85CB-FA163E7B75A4.root",
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/320/065/00000/CCB0AA1E-328E-E811-81D9-FA163E690F64.root",
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/319/950/00000/0CD386E8-CC8B-E811-B9AE-FA163E9C8F11.root",
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/319/950/00000/E820FFA4-CD8B-E811-B5AD-02163E01481B.root",
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/320/006/00000/C40BD643-D68C-E811-A1FC-FA163ECCA032.root",
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/320/006/00000/E445FCAE-EA8C-E811-BD48-FA163EC78341.root",
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/320/006/00000/EEDC1086-D68C-E811-8D47-02163E01A053.root",
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/319/910/00000/1470C0AB-088B-E811-AEDE-FA163E22408B.root",
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/319/910/00000/265A2659-088B-E811-8C27-A4BF0112DB74.root",
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/319/849/00000/C8D52915-458A-E811-8D89-FA163EE9CF16.root",
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/319/849/00000/D6BA9D0D-458A-E811-8BD8-FA163EECA815.root",
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/319/348/00000/609FD88E-0D83-E811-9D85-FA163E3ECB15.root",
                                "/store/data/Run2018C/ZeroBias/RAW/v1/000/319/348/00000/C6FD98EF-0E83-E811-9BF1-02163E00AD83.root",
                            )
)

process.options = cms.untracked.PSet(
    FailPath = cms.untracked.vstring(),
    IgnoreCompletely = cms.untracked.vstring(),
    Rethrow = cms.untracked.vstring(),
    SkipEvent = cms.untracked.vstring(),
    allowUnscheduled = cms.obsolete.untracked.bool,
    canDeleteEarly = cms.untracked.vstring(),
    deleteNonConsumedUnscheduledModules = cms.untracked.bool(True),
    dumpOptions = cms.untracked.bool(False),
    emptyRunLumiMode = cms.obsolete.untracked.string,
    eventSetup = cms.untracked.PSet(
        forceNumberOfConcurrentIOVs = cms.untracked.PSet(
            allowAnyLabel_=cms.required.untracked.uint32
        ),
        numberOfConcurrentIOVs = cms.untracked.uint32(0)
    ),
    fileMode = cms.untracked.string('FULLMERGE'),
    forceEventSetupCacheClearOnNewRun = cms.untracked.bool(False),
    makeTriggerResults = cms.obsolete.untracked.bool,
    numberOfConcurrentLuminosityBlocks = cms.untracked.uint32(0),
    numberOfConcurrentRuns = cms.untracked.uint32(1),
    numberOfStreams = cms.untracked.uint32(4),
    numberOfThreads = cms.untracked.uint32(4),
    printDependencies = cms.untracked.bool(False),
    sizeOfStackForThreadsInKB = cms.optional.untracked.uint32,
    throwIfIllegalParameter = cms.untracked.bool(True),
    wantSummary = cms.untracked.bool(False)
)


from Configuration.AlCa.GlobalTag import GlobalTag
#process.GlobalTag = GlobalTag(process.GlobalTag, '106X_dataRun2_v35', '')
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_data', '')

# Path and EndPath definitions
process.endOfJobOut = cms.OutputModule(
    "PoolOutputModule",
    outputCommands = cms.untracked.vstring('keep *'),
    fileName = cms.untracked.string("file:./TestOut.root"),
)


process.raw2digi_step = cms.Path(process.RawToDigi)
#process.endjob_step = cms.EndPath(process.endOfProcess)
process.endjob_step = cms.EndPath(process.endOfJobOut)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step, process.endjob_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# customisation of the process.

# Automatic addition of the customisation function from L1Trigger.Configuration.customiseReEmul
from L1Trigger.Configuration.customiseReEmul import L1TReEmulFromRAW 

#call to customisation function L1TReEmulFromRAW imported from L1Trigger.Configuration.customiseReEmul
process = L1TReEmulFromRAW(process)

# Automatic addition of the customisation function from L1Trigger.L1TNtuples.customiseL1Ntuple
from L1Trigger.L1TNtuples.customiseL1Ntuple import L1NtupleRAWEMU 

#call to customisation function L1NtupleRAWEMU imported from L1Trigger.L1TNtuples.customiseL1Ntuple
process = L1NtupleRAWEMU(process)

# Automatic addition of the customisation function from L1Trigger.Configuration.customiseSettings
from L1Trigger.Configuration.customiseSettings import L1TSettingsToCaloParams_2018_v1_3 

#call to customisation function L1TSettingsToCaloParams_2018_v1_3 imported from L1Trigger.Configuration.customiseSettings
process = L1TSettingsToCaloParams_2018_v1_3(process)

process.TFileService = cms.Service(
	"TFileService",
	#fileName = cms.string("l1TNtuple-test.root")
    fileName = cms.string(options.outputFile)
)

# Production modules
process.load('L1Trigger.L1TCaloLayer1.uct2016EmulatorDigis_cfi')
process.load('anomalyDetection.anomalyTriggerSkunkworks.uGTADEmulator_cfi')
process.load('anomalyDetection.anomalyTriggerSkunkworks.pileupNetworkProducer_cfi')
process.load('anomalyDetection.miniCICADA.miniCICADAProducer_cfi')
# Analysis modules
process.load('anomalyDetection.miniCICADA.miniCICADAAnalyzer_cfi')
process.load('anomalyDetection.ZtoeePeakAnalysis.basicEventInfoAnalyzer_cfi')
process.load('anomalyDetection.ZtoeePeakAnalysis.electronInformationAnalyzer_cfi')
process.load('anomalyDetection.anomalyTriggerSkunkworks.L1TCaloSummaryTestNtuplizer_cfi')
process.L1TCaloSummaryTestNtuplizer.includePUInfo = cms.bool(True)
process.L1TCaloSummaryTestNtuplizer.ecalToken = cms.InputTag('simEcalTriggerPrimitiveDigis')
process.L1TCaloSummaryTestNtuplizer.hcalToken = cms.InputTag('simHcalTriggerPrimitiveDigis')
process.load('anomalyDetection.anomalyTriggerSkunkworks.L1TTriggerBitsNtuplizer_cfi')
process.load('anomalyDetection.anomalyTriggerSkunkworks.boostedJetTriggerNtuplizer_cfi')
process.load('anomalyDetection.anomalyTriggerSkunkworks.uGTModelNtuplizer_cfi')
process.load('anomalyDetection.anomalyTriggerSkunkworks.pileupNetworkNtuplizer_cfi')

process.productionTask = cms.Task(
    process.uct2016EmulatorDigis,
    process.uGTADEmulator,
    process.pileupNetworkProducer,
    process.miniCICADAProducer
)

process.analysisSequence = cms.Sequence(
    #MINIAOD based analyzers
    process.basicEventInfoAnalyzer + 
    process.miniCICADAAnalyzer + 
    process.electronInformationAnalyzer +
    #RAW based analysers
    process.L1TCaloSummaryTestNtuplizer +
    process.L1TTriggerBitsNtuplizer +
    process.boostedJetTriggerNtuplizer +
    process.uGTModelNtuplizer +
    process.pileupNetworkNtuplizer
)

process.analysisStep = cms.Path(process.analysisSequence, process.productionTask)
process.endjobStep = cms.Path(process.endOfProcess)

process.schedule.append(process.analysisStep)
process.schedule.append(process.endjobStep)

print(process.schedule)
print("**************************************************")
print([x for x in process.schedule])

#Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
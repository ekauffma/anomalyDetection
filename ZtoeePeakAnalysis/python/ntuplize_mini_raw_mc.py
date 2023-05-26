import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run2_2018_cff import Run2_2018
from Configuration.Eras.Era_Run3_cff import Run3

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
                            # child dataset: /DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL18MiniAODv2-PUForTRKv2_TRKv2_106X_upgrade2018_realistic_v16_L1v1-v2/MINIAODSIM
                            fileNames = cms.untracked.vstring("/store/mc/RunIISummer20UL18MiniAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUForTRKv2_TRKv2_106X_upgrade2018_realistic_v16_L1v1-v2/2530000/9E31C47D-7A5D-4141-8D2F-0BBC79F7B0CE.root"),
                            #parent dataset: /DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL18HLT-PUForTRKv2_TRKv2_102X_upgrade2018_realistic_v15-v2/GEN-SIM-DIGI-RAW
                            secondaryFileNames = cms.untracked.vstring(
                                "/store/mc/RunIISummer20UL18HLT/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/GEN-SIM-DIGI-RAW/PUForTRKv2_TRKv2_102X_upgrade2018_realistic_v15-v2/2530000/0A49E091-B0E8-D942-8823-ED8A5981D883.root",
                            ),
                            lumisToSkip=cms.untracked.VLuminosityBlockRange("1:23")
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
    numberOfStreams = cms.untracked.uint32(1),
    numberOfThreads = cms.untracked.uint32(1),
    printDependencies = cms.untracked.bool(False),
    sizeOfStackForThreadsInKB = cms.optional.untracked.uint32,
    throwIfIllegalParameter = cms.untracked.bool(True),
    wantSummary = cms.untracked.bool(False)
)


from Configuration.AlCa.GlobalTag import GlobalTag
#process.GlobalTag = GlobalTag(process.GlobalTag, '106X_dataRun2_v35', '')
#process.GlobalTag = GlobalTag(process.GlobalTag, '106X_upgrade2018_realistic_v11_L1v1', '') #this doesn't work?
process.GlobalTag = GlobalTag(process.GlobalTag, '124X_mcRun3_2022_realistic_v12', '') # this works for some reason?
#process.GlobalTag = GlobalTag(process.GlobalTag, '106X_upgrade2018_realistic_v16_L1v1', '')

# Path and EndPath definitions
process.raw2digi_step = cms.Path(process.RawToDigi)
process.endjob_step = cms.EndPath(process.endOfProcess)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step, process.endjob_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# customisation of the process.

# Automatic addition of the customisation function from L1Trigger.Configuration.customiseReEmul
from L1Trigger.Configuration.customiseReEmul import L1TReEmulMCFromRAW 

# #call to customisation function L1TReEmulFromRAW imported from L1Trigger.Configuration.customiseReEmul
process = L1TReEmulMCFromRAW(process)

# Automatic addition of the customisation function from L1Trigger.L1TNtuples.customiseL1Ntuple
from L1Trigger.L1TNtuples.customiseL1Ntuple import L1NtupleRAWEMUGEN_MC 

#call to customisation function L1NtupleRAWEMU imported from L1Trigger.L1TNtuples.customiseL1Ntuple
process = L1NtupleRAWEMUGEN_MC(process)

# Automatic addition of the customisation function from L1Trigger.Configuration.customiseSettings
# from L1Trigger.Configuration.customiseSettings import L1TSettingsToCaloParams_2018_v1_3 

# #call to customisation function L1TSettingsToCaloParams_2018_v1_3 imported from L1Trigger.Configuration.customiseSettings
# process = L1TSettingsToCaloParams_2018_v1_3(process)

from L1Trigger.Configuration.customiseSettings import L1TSettingsToCaloParams_2018_v1_4_1
process = L1TSettingsToCaloParams_2018_v1_4_1(process)

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
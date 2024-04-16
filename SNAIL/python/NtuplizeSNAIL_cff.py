import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run2_2018_cff import Run2_2018

import FWCore.ParameterSet.VarParsing as VarParsing
options = VarParsing.VarParsing ('analysis')
options.parseArguments()

process = cms.Process("NTUPLIZE",Run2_2018)
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
process.MessageLogger.cerr.FwkReport.reportEvery = 10000

#attempt to get rid of muon shower warning
process.MessageLogger.suppressWarning = cms.untracked.vstring(
    'l1UpgradeTree',
    'l1UpgradeEmuTree',
    'l1UpgradeTfMuonShowerTree', 
    'emtfStage2Digis', 
    'l1uGTTestcrateTree', 
    'simDtTriggerPrimitiveDigis'
)

process.source = cms.Source("PoolSource",
                            # fileNames = cms.untracked.vstring('/store/data/Run2018D/EphemeralZeroBias2/MINIAOD/PromptReco-v2/000/320/497/00000/22EA8756-6395-E811-A29D-02163E019FE1.root'),
                            # secondaryFileNames = cms.untracked.vstring(
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/497/00000/128A5822-CA93-E811-9F04-FA163ECFF8BE.root',
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/497/00000/54967CD9-C893-E811-BE8B-FA163E085754.root',
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/497/00000/8437145A-CB93-E811-A6AD-FA163E222D2C.root',
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/497/00000/B48ECE7A-C893-E811-BFC7-FA163E33D73A.root',
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/497/00000/CC8A25EB-C993-E811-AB4A-FA163E48E52D.root',
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/497/00000/D2402298-C893-E811-8D87-02163E00CE99.root',
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/497/00000/F042C778-C893-E811-B840-FA163E365B83.root'
                            # )
                            # fileNames = cms.untracked.vstring('/store/data/Run2018D/EphemeralZeroBias2/MINIAOD/PromptReco-v2/000/320/570/00000/280370FC-6496-E811-833E-FA163E80C350.root'),
                            # secondaryFileNames = cms.untracked.vstring(
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/570/00000/16DFBFAF-8094-E811-8E3F-02163E019FF6.root',
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/570/00000/1827616B-7A94-E811-AF40-FA163E4BCD81.root',
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/570/00000/2EED80AC-8D94-E811-8BAD-FA163ECCE6F0.root',
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/570/00000/584A05BA-7994-E811-9DB8-FA163E3FE3C5.root',
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/570/00000/5E56BDCB-7F94-E811-92D9-FA163E990568.root',
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/570/00000/80CD42EA-7E94-E811-864C-FA163EBC5A2D.root',
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/570/00000/8E033345-7C94-E811-B4AF-FA163E3F4095.root',
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/570/00000/B2792A4F-7C94-E811-B14A-FA163EC1819D.root',
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/570/00000/D01BB388-8194-E811-910B-02163E017F52.root',
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/570/00000/E6C30D4D-7C94-E811-AABA-FA163EF21D25.root',
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/570/00000/E83578F9-8294-E811-B2FA-FA163E376DA0.root',
                            #     '/store/data/Run2018D/EphemeralZeroBias2/RAW/v1/000/320/570/00000/FA84DB3F-7D94-E811-B8B7-FA163E793AC1.root',
                            fileNames = cms.untracked.vstring(
                                "/store/mc/Run3Summer23BPixMiniAODv4/GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v2-v2/50000/0079d759-4ab1-4c8b-b903-f9b9665e7390.root",
                            ),
                            secondaryFileNames = cms.untracked.vstring(
                                "/store/mc/Run3Summer23BPixDRPremix/GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8/GEN-SIM-RAW/130X_mcRun3_2023_realistic_postBPix_v2-v2/50000/83ea0f0b-461f-4b80-b791-739ba1dd703c.root",
                                "/store/mc/Run3Summer23BPixDRPremix/GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8/GEN-SIM-RAW/130X_mcRun3_2023_realistic_postBPix_v2-v2/50000/863e4b5e-ca57-4e95-917f-dde67df11ec2.root",
                                "/store/mc/Run3Summer23BPixDRPremix/GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8/GEN-SIM-RAW/130X_mcRun3_2023_realistic_postBPix_v2-v2/50000/965f0438-e597-4c20-bca3-93feb984b2aa.root",
                                "/store/mc/Run3Summer23BPixDRPremix/GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8/GEN-SIM-RAW/130X_mcRun3_2023_realistic_postBPix_v2-v2/50000/e048b964-42bf-40b2-a379-3d9a89d13ec9.root",
                                "/store/mc/Run3Summer23BPixDRPremix/GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8/GEN-SIM-RAW/130X_mcRun3_2023_realistic_postBPix_v2-v2/50000/17b202b9-dcfd-4dd6-bdfa-1ac54155da86.root",
                                "/store/mc/Run3Summer23BPixDRPremix/GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8/GEN-SIM-RAW/130X_mcRun3_2023_realistic_postBPix_v2-v2/50000/19f9e7d6-c2fb-4d22-bef8-479a36e3c47e.root",
                                "/store/mc/Run3Summer23BPixDRPremix/GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8/GEN-SIM-RAW/130X_mcRun3_2023_realistic_postBPix_v2-v2/50000/a9056e74-4a6d-4b81-9b88-07278a952a3f.root",
                                "/store/mc/Run3Summer23BPixDRPremix/GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8/GEN-SIM-RAW/130X_mcRun3_2023_realistic_postBPix_v2-v2/50000/e2ec7876-be68-4677-a7dd-da9c39ce2ed9.root",
                                "/store/mc/Run3Summer23BPixDRPremix/GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8/GEN-SIM-RAW/130X_mcRun3_2023_realistic_postBPix_v2-v2/50000/01837555-74cd-4d06-9e31-b99e08287c51.root",
                            )

)

process.options = cms.untracked.PSet(
    #FailPath = cms.untracked.vstring(),
    IgnoreCompletely = cms.untracked.vstring(),
    Rethrow = cms.untracked.vstring(),
    #SkipEvent = cms.untracked.vstring(),
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
    numberOfStreams = cms.untracked.uint32(0),
    numberOfThreads = cms.untracked.uint32(1),
    printDependencies = cms.untracked.bool(False),
    sizeOfStackForThreadsInKB = cms.optional.untracked.uint32,
    throwIfIllegalParameter = cms.untracked.bool(True),
    wantSummary = cms.untracked.bool(False)
)

from Configuration.AlCa.GlobalTag import GlobalTag
#process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_data', '')
process.GlobalTag = GlobalTag(process.GlobalTag, '130X_mcRun3_2023_realistic_postBPix_v2', '')

process.raw2digi_step = cms.Path(process.RawToDigi)
process.endjob_step = cms.EndPath(process.endOfProcess)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step, process.endjob_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

#Setup FWK for multithreaded
process.options.numberOfThreads = 1
process.options.numberOfStreams = 1
process.options.numberOfConcurrentLuminosityBlocks = 1
process.options.eventSetup.numberOfConcurrentIOVs = 1
if hasattr(process, 'DQMStore'): process.DQMStore.assertLegacySafe=cms.untracked.bool(False)
# Automatic addition of the customisation function from L1Trigger.Configuration.customiseReEmul
from L1Trigger.Configuration.customiseReEmul import L1TReEmulFromRAW 

#call to customisation function L1TReEmulFromRAW imported from L1Trigger.Configuration.customiseReEmul
process = L1TReEmulFromRAW(process)

# Automatic addition of the customisation function from L1Trigger.L1TNtuples.customiseL1Ntuple
from L1Trigger.L1TNtuples.customiseL1Ntuple import L1NtupleRAWEMU 

#call to customisation function L1NtupleRAWEMU imported from L1Trigger.L1TNtuples.customiseL1Ntuple
process = L1NtupleRAWEMU(process)


# Automatic addition of the custcomparison function Compareomisation function from L1Trigger.Configuration.customiseSettings
#from L1Trigger.Configuration.customiseSettings import L1TSettingsToCaloParams_2018_v1_4
# from L1Trigger.Configuration.customiseSettings import L1TSettingsToCaloParams_2018_v1_4_NoPUS

#call to customisation function L1TSettingsToCaloParams_2018_v1_3 imported from L1Trigger.Configuration.customiseSettings
#process = L1TSettingsToCaloParams_2018_v1_4(process)
# process = L1TSettingsToCaloParams_2018_v1_4_NoPUS(process)

from anomalyDetection.SNAIL.L1RegionNtuplizer_cfi import L1RegionNtuplizer
from anomalyDetection.SNAIL.puppiJetNtuplizer_cfi import puppiJetNtuplizer
from anomalyDetection.SNAIL.PUVertexNtuplizer_cfi import PUVertexNtuplizer
process.L1RegionNtuplizer = L1RegionNtuplizer
process.puppiJetNtuplizer = puppiJetNtuplizer
process.PUVertexNtuplizer = PUVertexNtuplizer

process.customNtuplePath = cms.Path(
    process.L1RegionNtuplizer + 
    process.puppiJetNtuplizer +
    process.PUVertexNtuplizer
)

process.schedule.append(process.customNtuplePath)

process.TFileService = cms.Service(
	"TFileService",
	#fileName = cms.string("l1TNtuple-test.root")
        fileName = cms.string(options.outputFile)
)

print("schedule:")
print(process.schedule)
print("schedule contents:")
print([x for x in process.schedule])

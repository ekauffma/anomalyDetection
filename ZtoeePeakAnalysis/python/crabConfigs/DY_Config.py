from CRABClient.UserUtilities import config
import os
import datetime

config = config()
todaysDate = datetime.date.today().strftime('%d%b%Y')

config.General.requestName = f'ZtoeePeak_RAW_MINI_DY_{todaysDate}'
config.General.workArea = 'crabWorkArea'
config.General.transferOutput = True

config.JobType.pluginname = 'Analysis'
config.JobType.psetName = f'{os.environ["CMSSW_BASE"]}/src/anomalyDetection/ZtoeePeakAnalysis/python/ntuplize_mini_raw_mc.py'
config.JobType.maxMemoryMB = 4000
cicadaPath = f'{os.environ["CMSSW_BASE"]}/src/anomalyDetection/CICADA'
if os.path.isdir(cicadaPath):
    config.JobType.inputFiles=[cicadaPath]

config.Data.inputDataset = '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL18MiniAODv2-PUForTRKv2_TRKv2_106X_upgrade2018_realistic_v16_L1v1-v2/MINIAODSIM'
config.Data.secondaryInputDataset = '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL18HLT-PUForTRKv2_TRKv2_102X_upgrade2018_realistic_v15-v2/GEN-SIM-DIGI-RAW'
config.Data.inputDBS = 'global'
#config.Data.lumiMask = 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions18/13TeV/Legacy_2018/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt'
config.Data.publication = False
config.Data.outputDatasetTag = f'CICADA_Ztoee_wMINIAOD_RAW_DY_{todaysDate}'

config.Site.storageSite = 'T2_US_Wisconsin'
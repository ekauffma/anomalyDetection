from CRABClient.UserUtilities import config
import os
import datetime

config = config()
todaysDate = datetime.date.today().strftime('%d%b%Y')

config.General.requestName = f'ZtoeePeak_RAW_MINI_RunD_{todaysDate}'
config.General.workArea = 'crabWorkArea'
config.General.transferOutput = True

config.JobType.pluginname = 'Analysis'
config.JobType.psetName = f'{os.environ["CMSSW_BASE"]}/src/anomalyDetection/ZtoeePeakAnalysis/python/ntuplize_mini_raw.py'
config.JobType.maxMemoryMB = 8000
config.JobType.numCores = 4
cicadaPath = f'{os.environ["CMSSW_BASE"]}/src/anomalyDetection/CICADA'
if os.path.isdir(cicadaPath):
    config.JobType.inputFiles=[cicadaPath]

config.Data.inputDataset = '/ZeroBias/Run2018D-UL2018_MiniAODv2-v1/MINIAOD'
config.Data.secondaryInputDataset = '/ZeroBias/Run2018D-v1/RAW'
config.Data.inputDBS = 'global'
#config.Data.lumiMask = 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions18/13TeV/Legacy_2018/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt'
config.Data.publication = False
config.Data.outputDatasetTag = f'CICADA_Ztoee_wMINIAOD_RAW_RunD_{todaysDate}'

config.Site.storageSite = 'T2_US_Wisconsin'
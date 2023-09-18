from CRABClient.UserUtilities import config
import os
import datetime

config = config()
todaysDate = datetime.date.today().strftime('%d%b%Y')

config.General.requestName = f'SNAIL_2018RunB_ZB_{todaysDate}'
config.General.workArea = 'crabWorkArea'
config.General.transferOutputs = True

config.JobType.pluginname = 'Analysis'
config.JobType.psetName = f'{os.environ["CMSSW_BASE"]}/src/anomalyDetection/SNAIL/python/NtuplizeSNAIL_cff.py'
config.JobType.maxMemoryMB = 4000

config.Data.inputDataset = '/ZeroBias/Run2018B-UL2018_MiniAODv2-v1/MINIAOD'
config.Data.secondaryInputDataset = '/ZeroBias/Run2018B-v1/RAW'
config.Data.inputDBS = 'global'
config.Data.splitting = 'Automatic'
config.Data.publication = False
config.Data.outputDatasetTag = f'SNAIL_2018RunB_ZB_{todaysDate}'

config.Site.storageSite = 'T2_US_Wisconsin'
import os
import datetime
from CRABClient.UserUtilities import config
config = config()

todaysDate = datetime.date.today().strftime('%Y%m%d')

config.General.requestName = f'CICADA_Pileup_ZeroBias_Run2023E_v1_{todaysDate}'
config.General.transferOutputs = True
config.General.transferLogs = True
config.General.workArea = 'crabWorkArea'

config.JobType.allowUndistributedCMSSW = True
config.JobType.psetName = f'{os.environ["CMSSW_BASE"]}/src/anomalyDetection/paperCode/python/makeCICADANtuplesFromRAW_withNPV.py'
config.JobType.pluginName = 'Analysis'
config.JobType.outputFiles = ['out_hist.root']
config.Data.outLFNDirBase = '/store/user/ekauffma'

config.JobType.maxMemoryMB = 4000


config.Data.inputDataset = '/ZeroBias/Run2023E-PromptReco-v1/MINIAOD'
config.Data.secondaryInputDataset = '/ZeroBias/Run2023E-v1/RAW'
config.Data.inputDBS = 'global'
config.Data.splitting = 'Automatic'
config.Data.publication = False
config.Data.outputDatasetTag = f'CICADA_Pileup_ZeroBias_Run2023E_v1_{todaysDate}'

config.Site.storageSite = 'T2_US_Wisconsin'

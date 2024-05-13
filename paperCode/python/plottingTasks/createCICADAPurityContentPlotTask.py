from anomalyDetection.paperCode.plottingCore.plotTask import createPlotTask

import ROOT
from anomalyDetection.paperCode.plottingUtilities.models import *
from pathlib import Path
from anomalyDetection.paperCode.plottingUtilities.scoreMaxAndMins import scoreMaxAndMinHelper
from anomalyDetection.paperCode.plottingUtilities.rateTables import rateTableHelper

class createCICADAPurityContentPlotTask(createPlotTask):
    def __init__(
            self,
            taskName: str,
            outputFileName: str,
            dictOfSamples: dict,
            outputPath: Path = Path("/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/"),
            nBins: int = 40,
            rates: list[float] = [3.0,],
    ):
        super().__init__(
            taskName,
            outputFileName,
            dictOfSamples,
            outputPath,
        )
        self.scoreMaxAndMins = scoreMaxAndMinHelper()
        self.rateTable = rateTableHelper()
        self.nBins = nBins
        self.rates = rates
        
        self.multiEGTriggerList = [
            'L1_DoubleEG8er2p5_HTT300er',
            'L1_DoubleEG8er2p5_HTT320er',
            'L1_DoubleEG8er2p5_HTT340er',
            'L1_DoubleEG_25_12_er2p5',
            'L1_DoubleEG_25_14_er2p5',
            'L1_DoubleEG_27_14_er2p5',
            'L1_DoubleEG_LooseIso18_LooseIso12_er1p5',
            'L1_DoubleEG_LooseIso20_LooseIso12_er1p5',
            'L1_DoubleEG_LooseIso22_12_er2p5',
            'L1_DoubleEG_LooseIso22_LooseIso12_er1p5',
            'L1_DoubleEG_LooseIso25_12_er2p5',
            'L1_DoubleEG_LooseIso25_LooseIso12_er1p5',
            'L1_DoubleLooseIsoEG22er2p1',
            'L1_DoubleLooseIsoEG24er2p1',
            'L1_TripleEG_18_17_8_er2p5',
            'L1_TripleEG_18_18_12_er2p5',
        ]

        self.multiTauTriggerList = [
            'L1_DoubleIsoTau26er2p1_Jet70_RmOvlp_dR0p5',
            'L1_DoubleIsoTau34er2p1',
            'L1_DoubleIsoTau35er2p1',
            'L1_DoubleIsoTau36er2p1',
            'L1_DoubleTau70er2p1',
        ]

        self.multiJetTriggerList = [
            'L1_DoubleJet112er2p3_dEta_Max1p6',
            'L1_DoubleJet150er2p5',
            'L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5',
            'L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5',
            'L1_DoubleJet30er2p5_Mass_Min360_dEta_Max1p5',
            'L1_DoubleJet35_Mass_Min450_IsoTau45er2p1_RmOvlp_dR0p5',
            'L1_DoubleJet40_Mass_Min450_LooseIsoEG15er2p1_RmOvlp_dR0p2',
            'L1_DoubleJet45_Mass_Min450_IsoTau45er2p1_RmOvlp_dR0p5',
            'L1_DoubleJet45_Mass_Min450_LooseIsoEG20er2p1_RmOvlp_dR0p2',
            'L1_DoubleJet_100_30_DoubleJet30_Mass_Min800',
            'L1_DoubleJet_110_35_DoubleJet35_Mass_Min620',
            'L1_DoubleJet_110_35_DoubleJet35_Mass_Min800',
            'L1_DoubleJet_115_40_DoubleJet40_Mass_Min620',
            'L1_DoubleJet_115_40_DoubleJet40_Mass_Min620_Jet60TT28',
            'L1_DoubleJet_120_45_DoubleJet45_Mass_Min620',
            'L1_DoubleJet_120_45_DoubleJet45_Mass_Min620_Jet60TT28',
            'L1_DoubleJet_60_30_DoubleJet30_Mass_Min500_DoubleJetCentral50',
            'L1_DoubleJet_65_30_DoubleJet30_Mass_Min400_ETMHF65',
            'L1_DoubleJet_65_35_DoubleJet35_Mass_Min500_DoubleJetCentral50',
            'L1_DoubleJet_70_35_DoubleJet35_Mass_Min400_ETMHF65',
            'L1_DoubleJet_80_30_DoubleJet30_Mass_Min500_Mu3OQ',
            'L1_DoubleJet_85_35_DoubleJet35_Mass_Min500_Mu3OQ',
            'L1_DoubleJet_90_30_DoubleJet30_Mass_Min800',
            'L1_DoubleLLPJet40',
            'L1_QuadJet_95_75_65_20_DoubleJet_75_65_er2p5_Jet20_FWD3p0',
            'L1_TripleJet_100_80_70_DoubleJet_80_70_er2p5',
            'L1_TripleJet_105_85_75_DoubleJet_85_75_er2p5',
            'L1_TripleJet_95_75_65_DoubleJet_75_65_er2p5',
        ]
        
        self.multiMuTriggerList = [
            'L1_DoubleMu0_Upt15_Upt7',
            'L1_DoubleMu0_Upt6_IP_Min1_Upt4',
            'L1_DoubleMu0_dR_Max1p6_Jet90er2p5_dR_Max0p8',
            'L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4',
            'L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4',
            'L1_DoubleMu18er2p1_SQ',
            'L1_DoubleMu3_OS_er2p3_Mass_Max14_DoubleEG7p5_er2p1_Mass_Max20',
            'L1_DoubleMu3_SQ_ETMHF40_HTT60er',
            'L1_DoubleMu3_SQ_ETMHF40_Jet60er2p5_OR_DoubleJet40er2p5',
            'L1_DoubleMu3_SQ_ETMHF50_HTT60er',
            'L1_DoubleMu3_SQ_ETMHF50_Jet60er2p5',
            'L1_DoubleMu3_SQ_ETMHF50_Jet60er2p5_OR_DoubleJet40er2p5',
            'L1_DoubleMu3_SQ_ETMHF60_Jet60er2p5',
            'L1_DoubleMu3_SQ_HTT220er',
            'L1_DoubleMu3_SQ_HTT240er',
            'L1_DoubleMu3_SQ_HTT260er',
            'L1_DoubleMu3_dR_Max1p6_Jet90er2p5_dR_Max0p8',
            'L1_DoubleMu3er2p0_SQ_OS_dR_Max1p6',
            'L1_DoubleMu4_SQ_OS_dR_Max1p2',
            'L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6',
            'L1_DoubleMu4p5_SQ_OS_dR_Max1p2',
            'L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18',
            'L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7',
            'L1_DoubleMu5_OS_er2p3_Mass_8to14_DoubleEG3er2p1_Mass_Max20',
            'L1_DoubleMu5_SQ_EG9er2p5',
            'L1_DoubleMu8_SQ',
            'L1_DoubleMu9_SQ',
            'L1_DoubleMu_15_5_SQ',
            'L1_DoubleMu_15_7',
            'L1_DoubleMu_15_7_SQ',
            'L1_TripleMu3_SQ',
            'L1_TripleMu_3SQ_2p5SQ_0_OS_Mass_Max12',
            'L1_TripleMu_4SQ_2p5SQ_0_OS_Mass_Max12',
            'L1_TripleMu_5SQ_3SQ_0OQ_DoubleMu_5_3_SQ_OS_Mass_Max9',
            'L1_TripleMu_5SQ_3SQ_0_DoubleMu_5_3_SQ_OS_Mass_Max9',
            'L1_TripleMu_5_3_3',
            'L1_TripleMu_5_3_3_SQ',
            'L1_TripleMu_5_3p5_2p5_DoubleMu_5_2p5_OS_Mass_5to17',
            'L1_TripleMu_5_4_2p5_DoubleMu_5_2p5_OS_Mass_5to17',
            'L1_TripleMu_5_5_3',
        ]
        
        self.sumTriggers = [
            'L1_ETM150',
            'L1_ETMHF100',
            'L1_ETMHF100_HTT60er',
            'L1_ETMHF110',
            'L1_ETMHF110_HTT60er',
            'L1_ETMHF120',
            'L1_ETMHF120_HTT60er',
            'L1_ETMHF130',
            'L1_ETMHF130_HTT60er',
            'L1_ETMHF140',
            'L1_ETMHF150',
            'L1_ETMHF90',
            'L1_ETMHF90_HTT60er',
            'L1_ETMHF90_SingleJet60er2p5_dPhi_Min2p1',
            'L1_ETMHF90_SingleJet60er2p5_dPhi_Min2p6',
            'L1_ETMHF90_SingleJet80er2p5_dPhi_Min2p1',
            'L1_ETMHF90_SingleJet80er2p5_dPhi_Min2p6',
            'L1_ETT2000',
            'L1_HTT320er',
            'L1_HTT360er',
            'L1_HTT400er',
            'L1_HTT450er',
        ]

        self.sumPlusJetTriggers = [
            'L1_HTT200_SingleLLPJet60',
            'L1_HTT240_SingleLLPJet70',
            'L1_HTT320er_QuadJet_70_55_40_40_er2p5',
            'L1_HTT320er_QuadJet_80_60_er2p1_45_40_er2p3',
            'L1_HTT320er_QuadJet_80_60_er2p1_50_45_er2p3',

        ]

        self.tauPlusOtherTriggers = [
            'L1_LooseIsoEG22er2p1_IsoTau26er2p1_dR_Min0p3',
            'L1_LooseIsoEG22er2p1_Tau70er2p1_dR_Min0p3',
            'L1_LooseIsoEG24er2p1_IsoTau27er2p1_dR_Min0p3',
            'L1_Mu18er2p1_Tau24er2p1',
            'L1_Mu18er2p1_Tau26er2p1',
            'L1_Mu18er2p1_Tau26er2p1_Jet55',
            'L1_Mu18er2p1_Tau26er2p1_Jet70',
            'L1_Mu22er2p1_IsoTau32er2p1',
            'L1_Mu22er2p1_IsoTau34er2p1',
            'L1_Mu22er2p1_IsoTau36er2p1',
            'L1_Mu22er2p1_IsoTau40er2p1',
            'L1_Mu22er2p1_Tau70er2p1',
        ]

        self.egPlusJetOrSumTriggers = [
            'L1_LooseIsoEG28er2p1_HTT100er',
            'L1_LooseIsoEG28er2p1_Jet34er2p5_dR_Min0p3',
            'L1_LooseIsoEG30er2p1_HTT100er',
            'L1_LooseIsoEG30er2p1_Jet34er2p5_dR_Min0p3',
        ]

        self.muPlusJetOrSumTriggers = [
            'L1_Mu12er2p3_Jet40er2p1_dR_Max0p4_DoubleJet40er2p1_dEta_Max1p6',
            'L1_Mu12er2p3_Jet40er2p3_dR_Max0p4_DoubleJet40er2p3_dEta_Max1p6',
            'L1_Mu3er1p5_Jet100er2p5_ETMHF40',
            'L1_Mu3er1p5_Jet100er2p5_ETMHF50',
            'L1_Mu6_HTT240er',
            'L1_Mu6_HTT250er',
        ]

        self.muPlusEGTriggers = [
            'L1_Mu20_EG10er2p5',
            'L1_Mu6_DoubleEG12er2p5',
            'L1_Mu6_DoubleEG15er2p5',
            'L1_Mu6_DoubleEG17er2p5',
            'L1_Mu7_EG20er2p5',
            'L1_Mu7_EG23er2p5',
            'L1_Mu7_LooseIsoEG20er2p5',
            'L1_Mu7_LooseIsoEG23er2p5',
        ]

        self.singleEGTriggers = [
             'L1_SingleEG36er2p5',
            'L1_SingleEG38er2p5',
            'L1_SingleEG40er2p5',
            'L1_SingleEG42er2p5',
            'L1_SingleEG45er2p5',
            'L1_SingleEG60',
            'L1_SingleIsoEG30er2p1',
            'L1_SingleIsoEG30er2p5',
            'L1_SingleIsoEG32er2p1',
            'L1_SingleIsoEG32er2p5',
            'L1_SingleIsoEG34er2p5',
        ]

        self.singleJetTriggers = [
            'L1_SingleJet180',
            'L1_SingleJet180er2p5',
            'L1_SingleJet200',
            'L1_SingleJet43er2p5_NotBptxOR_3BX',
            'L1_SingleJet46er2p5_NotBptxOR_3BX',
        ]

        self.singleMuTriggers = [
            'L1_SingleMu22',
            'L1_SingleMu25',
            'L1_SingleMuOpen_er1p1_NotBptxOR_3BX',
            'L1_SingleMuOpen_er1p4_NotBptxOR_3BX',
            'L1_SingleMuShower_Nominal',
            'L1_SingleMuShower_Tight',
        ]
        
        self.singleTauTriggers = [
            'L1_SingleTau120er2p1',
            'L1_SingleTau130er2p1',
        ]

    def calculateTriggerOverlaps(self, rateDF, triggerGroups):
        overlapCount = {}
        for group in triggerGroups:
            overlapCount[group] = rateDF.Filter(
                self.getOverlapString(triggerGroups[group])
            ).Count()
        return overlapCount
    
    def makeOverlapHist(self, overlapCounts, totalCount, score, rate):
        rateStr = str(rate).replace('.', 'p')
        overlapName = f'OverlapCounts_xxx_{score}_xxx_{rateStr}'
        totalName = f'TotalContents_xxx_{score}_xxx_{rateStr}'
        contentsName = f'OverlapContents_xxx_{score}_xxx_{rateStr}'

        triggerGroups = list(overlapCounts.keys())
        nBins = len(triggerGroups)
        
        overlapHist = ROOT.TH1D(
            overlapName,
            overlapName,
            nBins,
            0.0,
            nBins,
        )
        totalHist = ROOT.TH1D(
            totalName,
            totalName,
            nBins,
            0.0,
            nBins
        )

        for index, triggerGroup in enumerate(triggerGroups):
            overlapHist.Fill(
                index,
                overlapCounts[triggerGroup]
            )
            totalHist.Fill(
                index,
                totalCount
            )
            overlapHist.GetXaxis().SetBinLabel(index+1, triggerGroup)
            totalHist.GetXaxis().SetBinLabel(index+1, triggerGroup)
        overlapContentsHist = overlapHist.Clone()
        overlapContentsHist.SetNameTitle(contentsName, contentsName)
        overlapContentsHist.Divide(totalHist)
        for index, triggerGroup in enumerate(triggerGroups):
            overlapContentsHist.GetXaxis().SetBinLabel(index+1, triggerGroup)
        overlapContentsHist.Scale(100.0)

        return overlapHist, totalHist, overlapContentsHist
        

    def getListOfTriggers(self, sampleDataframe):
        listOfColumns = sampleDataframe.GetColumnNames()
        listOfTriggers = [str(x) for x in listOfColumns if ('L1_' in str(x) and '_prescale' not in str(x))]
        listOfTriggers = [x.split('.')[1] for x in listOfTriggers]
        return listOfTriggers

    def getListOfUnprescaledTriggers(self, sampleDataframe):
        listOfTriggers = self.getListOfTriggers(sampleDataframe)
        counts = {}
        for trigger in listOfTriggers:
            prescaleColumn = f'{trigger}_prescale'
            counts[trigger] = sampleDataframe.Filter(f'{prescaleColumn} != 1').Count()
        for trigger in counts:
            counts[trigger] = counts[trigger].GetValue()
        result = []
        for trigger in counts:
            if counts[trigger] == 0:
                result.append(trigger)
        return result

    def getNoOverlapString(self, listOfTriggers):
        noOverlapString = ''
        for trigger in listOfTriggers:
            noOverlapString += f'{trigger} == 0 &&'
        noOverlapString = noOverlapString[:-2]
        return noOverlapString

    def getOverlapString(self, listOfTriggers):
        overlapString = ''
        for trigger in listOfTriggers:
            overlapString += f'{trigger} == 1 ||'
        overlapString = overlapString[:-2]
        return overlapString

    def noOverlapBooking(self, dataframe, sampleName, score, scoreMin, scoreMax, triggerGroup, triggerGroupName):
        histoName = f'{sampleName}_xxx_{score}_xxx_NoOverlap_xxx_{triggerGroupName}'
        theModel = ROOT.RDF.TH1DModel(
            histoName,
            histoName,
            self.nBins,
            scoreMin,
            scoreMax,
        )
        return dataframe.Filter(self.getNoOverlapString(triggerGroup)).Histo1D(theModel, score)

    def overlapBooking(self, dataframe, sampleName, score, scoreMin, scoreMax, triggerGroup, triggerGroupName):
        histoName = f'{sampleName}_xxx_{score}_xxx_Intersection_xxx_{triggerGroupName}'
        theModel = ROOT.RDF.TH1DModel(
            histoName,
            histoName,
            self.nBins,
            scoreMin,
            scoreMax,
        )
        return dataframe.Filter(self.getOverlapString(triggerGroup)).Histo1D(theModel, score)

    def totalBooking(self, dataframe, sampleName, score, scoreMin, scoreMax, triggergroup, triggerGroupName):
        histoName = f'{sampleName}_xxx_{score}_xxx_Total_xxx_{triggerGroupName}'
        theModel = ROOT.RDF.TH1DModel(
            histoName,
            histoName,
            self.nBins,
            scoreMin,
            scoreMax,
        )
        return dataframe.Histo1D(theModel, score)

    def makeAllScoreNamesFromGroups(self, listOfGroups):
        scoreNameList = []
        for group in listOfGroups:
            scoreNameList.append(group.adjustedTeacherScoreName)
            for studentModelName in group.studentModels:
                scoreNameList.append(group.studentModels[studentModelName].scoreName)
        return scoreNameList

    def createPlots(self):
        #okay... how are we going to do this?
        #I think our first step is to have plots of:
        #total CICADA score
        #pure CICADA score
        #overlap CICADA score
        #and overlap CICADA score for certain groups of unprescaled triggers
        cicadaScoreGroups = [
            CICADA_vXp2p0_Group,
            CICADA_vXp2p0N_Group,
            CICADA_vXp2p1_Group,
            CICADA_vXp2p1N_Group,
            CICADA_vXp2p2_Group,
            CICADA_vXp2p2N_Group,
        ]

        scoreNames = self.makeAllScoreNamesFromGroups(cicadaScoreGroups)
        scoreNames.append("CICADA_v2p1p2")

        allDFs = {}
        for sampleName in self.dictOfSamples:
            allDFs[sampleName] = self.dictOfSamples[sampleName].getNewDataframe()
            for group in cicadaScoreGroups:
                allDFs[sampleName] = group.applyFrameDefinitions(allDFs[sampleName])

        #Get score maxes and mins
        scoreMaxes, scoreMins = self.scoreMaxAndMins.getScoreMaxesAndMins(scoreNames, allDFs)

        #figure out what the unprescaled triggers are
        unprescaledTriggers = self.getListOfUnprescaledTriggers(allDFs['ZeroBias'])
        if 'L1_FirstBunchBeforeTrain' in unprescaledTriggers:
            unprescaledTriggers.remove('L1_FirstBunchBeforeTrain')
        
        triggerGroups = {
            'L1': unprescaledTriggers,
            'multiEG': self.multiEGTriggerList,
            'multiTau': self.multiTauTriggerList,
            'multiJet': self.multiJetTriggerList,
            'multiMu': self.multiMuTriggerList,
            'sums': self.sumTriggers,
            'sumsPlusJets': self.sumPlusJetTriggers,
            'tauPlusOther': self.tauPlusOtherTriggers,
            'egPlusJetOrSum': self.egPlusJetOrSumTriggers,
            'muPlusJetOrSum': self.muPlusJetOrSumTriggers,
            'muPlusEG': self.muPlusEGTriggers,
            'singleEG': self.singleEGTriggers,
            'singleJet': self.singleJetTriggers,
            'singleMuTriggers': self.singleMuTriggers,
            'singleTauTriggers': self.singleTauTriggers,
        }

        for sample in allDFs:
            for score in scoreNames:
                for triggerGroupName in triggerGroups:
                    self.plotsToBeWritten.append(
                        self.noOverlapBooking(
                            allDFs[sample],
                            sample,
                            score,
                            scoreMins[score],
                            scoreMaxes[score],
                            triggerGroups[triggerGroupName],
                            triggerGroupName
                        )
                    )
                    self.plotsToBeWritten.append(
                        self.overlapBooking(
                            allDFs[sample],
                            sample,
                            score,
                            scoreMins[score],
                            scoreMaxes[score],
                            triggerGroups[triggerGroupName],
                            triggerGroupName,
                        )
                    )
        for score in scoreNames:
            for desiredRate in self.rates:
                rateThreshold, trueRate = self.rateTable.getThresholdForRate(score, desiredRate)
                rateDF = allDFs['ZeroBias'].Filter(f'{score} > {rateThreshold}')
                overlaps = self.calculateTriggerOverlaps(rateDF, triggerGroups)
                totalCount = rateDF.Count()
                
                for triggerGroup in overlaps:
                    overlaps[triggerGroup] = overlaps[triggerGroup].GetValue()
                totalCount = totalCount.GetValue()

                overlapHist, totalHist, overlapContents = self.makeOverlapHist(overlaps, totalCount, score, desiredRate)
                self.plotsToBeWritten += [overlapHist, totalHist, overlapContents]

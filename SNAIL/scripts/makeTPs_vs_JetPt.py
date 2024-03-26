# Make an improved NTuple format for SNAIL
import ROOT
from time import perf_counter
import os
import math
import statistics
import random
import argparse

from rich.console import Console
from rich.progress import track
from rich.traceback import install
from rich.table import Table
install(show_locals=True)

from anomalyDetection.miniCICADA.scriptIncludes.iEtaiPhiBinning import iEtaiPhiBinCollection

console = Console()
iEtaiPhiMap = iEtaiPhiBinCollection()

class jet():
    def __init__(self, pt, eta, phi, m):
        self.pt = pt
        self.eta = eta
        self.phi = phi
        self.m = m
        self.lorentzVector = ROOT.TLorentzVector()
        self.lorentzVector.SetPtEtaPhiM(self.pt, self.eta, self.phi, self.m)
    
        self.iEta, self.iPhi = iEtaiPhiMap.iEtaiPhi(self.eta, self.phi)

    # def DeltaR(self, otherJet) -> float:
    #     return self.lorentzVector.DeltaR(otherJet.lorentzVector)
    def DeltaR(self, otherJet):
        deltaPhi = self.phi - otherJet.phi
        while deltaPhi < -1.0*math.pi:
            deltaPhi += math.pi
        while deltaPhi > math.pi:
            deltaPhi -= math.pi
        deltaEta = self.eta - otherJet.eta
        deltaR = math.sqrt(deltaPhi**2 + deltaEta**2)
        return deltaR

class puppiJet(jet):
    def __init__(self, theChain: ROOT.TChain, entryNum: int):
        super().__init__(
            theChain.ptVector[entryNum],
            theChain.etaVector[entryNum],
            theChain.phiVector[entryNum],
            theChain.massVector[entryNum],
        )

class triggerJet(jet):
    def __init__(self, theChain: ROOT.TChain, entryNum: int):
        super().__init__(
            theChain.L1Upgrade.jetEt[entryNum],
            theChain.L1Upgrade.jetEta[entryNum],
            theChain.L1Upgrade.jetPhi[entryNum],
            0.0
        )
        self.rawEt = theChain.L1Upgrade.jetRawEt[entryNum]
        self.puEt = theChain.L1Upgrade.jetPUEt[entryNum]
        self.seedEt = theChain.L1Upgrade.jetSeedEt[entryNum]
        self.BX = theChain.L1Upgrade.jetBx[entryNum]
        self.HWQuality = theChain.L1Upgrade.jetHwQual[entryNum]

class noPUTriggerJet(triggerJet):
    def __init__(self, theChain: ROOT.TChain, entryNum: int):
        super().__init__(theChain, entryNum)
        self.lorentzVector.SetPtEtaPhiM(
            self.rawEt * 0.5,
            self.eta,
            self.phi,
            0.0
        )
        

class eventData():
    def __init__(self, theChain: ROOT.TChain):
        self.chain = theChain
        self.matchedJets, self.unmatchedTriggerJets, self.unmatchedPuppiJets = createMatchedAndUnmatchedJets(*createTriggerAndPuppiJets(self.chain))
        self.nECALTP = self.chain.CaloTP.nECALTP
        self.nHCALTP = self.chain.CaloTP.nHCALTP
        self.totalTP = self.nECALTP + self.nHCALTP
        self.totalTPEnergy = 0.0
        for i in range(self.nECALTP):
            self.totalTPEnergy += self.chain.CaloTP.ecalTPet[i]
        for i in range(self.nHCALTP):
            self.totalTPEnergy += self.chain.CaloTP.hcalTPet[i]

    def findMatchedJetEnergyDifferences(self):
        etDeltas = []
        for triggerJet, puppiJet in self.matchedJets:
            etDeltas.append(puppiJet.lorentzVector.Et()-triggerJet.lorentzVector.Et())
        return etDeltas

def createTriggerAndPuppiJets(theChain):
    triggerJets = []
    puppiJets = []

    for entryNum in range(theChain.nObjects):
        puppiJets.append(puppiJet(theChain, entryNum))
    for entryNum in range(theChain.L1Upgrade.nJets):
        triggerJets.append(noPUTriggerJet(theChain, entryNum))
    
    return triggerJets, puppiJets

# basic idea here, pick a puppi jet
# find all trigger jets within 0.4 of it
# If there are none, this puppi jet is unmatched.
# Select this highest pt trigger jet
# these two are now matched, remove them from their lists
# Then we move on to the next
# At the end of this we hand back matched pairs, and unmatched jets
def createMatchedAndUnmatchedJets(triggerJets, puppiJets):
    unmatchedPuppiJets = []
    unmatchedTriggerJets = triggerJets
    matchedJets = []
    for puppiJetIndex, puppiJet in enumerate(puppiJets):
        distances = []
        for triggerJetIndex, triggerJet in enumerate(unmatchedTriggerJets):
            distances.append((triggerJetIndex, puppiJet.DeltaR(triggerJet)))
        distances.sort(key=lambda x: x[1])
        # Sort the distances, and remove any trigger jets that don't meet our criteria.
        for i in range(len(distances)):
            if distances[i][1] > 0.4:
                distances = distances[:i]
                break
        # if we have no appropriate trigger jets at this point, this is an unmatched puppi jet
        if len(distances) == 0:
            unmatchedPuppiJets.append(puppiJet)
            continue
        # Now we go through and check trigger jet pts
        # We will accept the highest one.
        highestPt = 0.0
        highestIndex = None
        for triggerJetIndex, DeltaR in distances:
            if unmatchedTriggerJets[triggerJetIndex].pt > highestPt:
                highestIndex = triggerJetIndex
        triggerJet = unmatchedTriggerJets.pop(highestIndex)
        matchedJets.append((triggerJet, puppiJet))
    return matchedJets, unmatchedTriggerJets, unmatchedPuppiJets

def makeAverageHistograms(energyDeltaHist, nMatchedPairsHist, nameTitle):
    averageHist = energyDeltaHist.Clone()
    averageHist.Divide(nMatchedPairsHist)

    averageHist.SetName(nameTitle)
    averageHist.SetName(nameTitle)

    return averageHist

def makeDebugTable(averagePlot, minX, maxX, nBins, columnName):
    outputTable = Table(title="Average(Pupppi ET - Trigger ET)")
    outputTable.add_column(columnName, justify="center")
    outputTable.add_column("Energy Delta", justify="center")

    for i in range (1, averageHist.GetNbinsX()+1):
        rangeLow = int((i-1)*(maxX-minX)/nBins)
        rangeHigh = int(i*(maxX-minX)/nBins)
        energyDelta = averagePlot.GetBinContent(i)
        outputTable.add_row(f"{rangeLow}-{rangeHigh}", f'{energyDelta}')

    console.print(outputTable)
    
def main(args):
    filePaths = [
        "/hdfs/store/user/aloelige/EphemeralZeroBias0/SNAIL_2023RunD_EZB0_18Oct2023/231018_205626/",
        # "/hdfs/store/user/aloelige/EphemeralZeroBias2/SNAIL_2023RunD_EZB2_18Oct2023/231018_205829/",
        "/hdfs/store/user/aloelige/EphemeralZeroBias2/SNAIL_2023RunD_EZB2_19Oct2023/231019_080917/",
        "/hdfs/store/user/aloelige/EphemeralZeroBias3/SNAIL_2023RunD_EZB3_18Oct2023/231018_205910/",
        "/hdfs/store/user/aloelige/EphemeralZeroBias4/SNAIL_2023RunD_EZB4_18Oct2023/231018_205953/",
        "/hdfs/store/user/aloelige/EphemeralZeroBias5/SNAIL_2023RunD_EZB5_18Oct2023/231018_210031/",
        "/hdfs/store/user/aloelige/EphemeralZeroBias6/SNAIL_2023RunD_EZB6_18Oct2023/231018_210109/",
        "/hdfs/store/user/aloelige/EphemeralZeroBias7/SNAIL_2023RunD_EZB7_19Oct2023/231019_080954/",
    ]
    
    allFiles = []
    for path in filePaths:
        console.print(f'Path: {path}')
        for dirpath, _ , fileNames in os.walk(path):
            for fileName in fileNames:
                allFiles.append(dirpath+'/'+fileName)
    console.print(f'Total number of files: {len(allFiles)}')

    eventChain = ROOT.TChain('l1EventTree/L1EventTree')
    puppiJetChain = ROOT.TChain('puppiJetNtuplizer/PuppiJets')
    triggerJetChain = ROOT.TChain('l1UpgradeEmuTree/L1UpgradeTree')
    regionChain = ROOT.TChain('L1RegionNtuplizer/L1EmuRegions')
    towerChain = ROOT.TChain('l1CaloTowerTree/L1CaloTowerTree')
    for fileName in track(allFiles, description="Adding files..."):
        eventChain.Add(fileName)
        puppiJetChain.Add(fileName)
        triggerJetChain.Add(fileName)
        regionChain.Add(fileName)
        towerChain.Add(fileName)
    eventChain.AddFriend(puppiJetChain)
    eventChain.AddFriend(triggerJetChain)
    eventChain.AddFriend(regionChain)
    eventChain.AddFriend(towerChain)

    # df = ROOT.RDataFrame(eventChain)

    # console.print(f'Available columns: \n{df.GetColumnNames()}')
    

    numEvents = eventChain.GetEntries()
    if args.maxEvents is not None:
        numEvents = min(numEvents, args.maxEvents)
    console.print(f'Processing {numEvents} events...', style='underline')

    #histogram counting number of jets per nECAL/nHCAL TPs
    nBins = 10
    minTPs = 0.0
    maxTPs = 2000.0

    minTPEnergy = 0.0
    maxTPEnergy = 4000.0

    nMatchedPairsHist = ROOT.TH1D(
        "nMatchedPairsHist",
        "nMatchedPairsHist",
        nBins,
        minTPs,
        maxTPs
    )
    #histogram weighted by the energy delta
    energyDeltasHist = ROOT.TH1D(
        "energyDeltasHist",
        "energyDeltasHist",
        nBins,
        minTPs,
        maxTPs
    )

    nMatchedPairs_TPET_Hist = ROOT.TH1D(
        "nMatchedPairs_TPET_Hist",
        "nMatchedPairs_TPET_Hist",
        nBins,
        minTPEnergy,
        maxTPEnergy,
    )
    energyDeltas_TPET_Hist = ROOT.TH1D(
        "energyDeltas_TPET_Hist",
        "energyDeltas_TPET_Hist",
        nBins,
        minTPEnergy,
        maxTPEnergy,
    )

    for i in track(range(numEvents), description="Scrolling events"):
    #for i in track(range(100), description="scrolling events"):
        # Grab the event
        eventChain.GetEntry(i)

        event = eventData(eventChain)

        if event.matchedJets == []: #if we have no matched jets, we're done here
            continue

        #let's figure out how many matched jets we have and the number of TPs
        nMatchedJets = len(event.matchedJets)
        totalTPs = event.totalTP

        #fill the histogram with the number of jets we got for this number of TPs
        nMatchedPairsHist.Fill(totalTPs, nMatchedJets)

        #let's find the differences between matched jets in the event data
        energyDeltas = event.findMatchedJetEnergyDifferences()
        #let's find the total energy delta
        energyDelta = sum(energyDeltas)
        
        #now let's fill the histogram
        energyDeltasHist.Fill(totalTPs, energyDelta)

        totalTPEnergy = event.totalTPEnergy
        nMatchedPairs_TPET_Hist.Fill(totalTPEnergy, nMatchedJets)
        energyDeltas_TPET_Hist.Fill(totalTPEnergy, energyDelta)
    
    #then to get average, you divide the bins of the energy deltas hist
    #by the bin contents of the number of matched jets hists
    averageJetEnergyDelta = makeAverageHistograms(energyDeltasHist, nMatchedPairsHist, "AverageJetEnergyDelta")
    averageJetEnergyDelta_TPET = makeAverageHistograms(energyDeltas_TPET_Hist, nMatchedPairs_TPET_Hist, "AverageJetEnergyDelta_TPET")


    makeDebugTable(averageJetEnergyDelta, minTPs, maxTPs, nBins, "nTPs")

    makeDebugTable(averageJetEnergyDelta_TPET, minTPEnergy, maxTPEnergy, nBins, "Total TP Energy")        

    outputFile = ROOT.TFile("./averageJetEnergyFile.root", "RECREATE")
    nMatchedPairsHist.Write()
    energyDeltasHist.Write()
    averageJetEnergyDelta.Write()
    
    nMatchedPairs_TPET_Hist.Write()
    energyDeltas_TPET_Hist.Write()
    averageJetEnergyDelta_TPET.Write()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Make Jet Delta vs nTPs")

    parser.add_argument(
        "--maxEvents",
        "-m",
        type=int,
        default=None,
    )

    args=parser.parse_args()

    main(args)

# Make an improved NTuple format for SNAIL
# REQUIRES NUMBA
import ROOT
# from numba import *
from time import perf_counter
import os
import math
import statistics
import random

from rich.console import Console
from rich.progress import track
from rich.traceback import install
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

# @jit
def createTriggerAndPuppiJets(theChain):
    triggerJets = []
    puppiJets = []

    for entryNum in range(theChain.nObjects):
        puppiJets.append(puppiJet(theChain, entryNum))
    for entryNum in range(theChain.L1Upgrade.nJets):
        triggerJets.append(triggerJet(theChain, entryNum))
    
    return triggerJets, puppiJets

# basic idea here, pick a puppi jet
# find all trigger jets within 0.4 of it
# If there are none, this puppi jet is unmatched.
# Select this highest pt trigger jet
# these two are now matched, remove them from their lists
# Then we move on to the next
# At the end of this we hand back matched pairs, and unmatched jets
# @njit
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

def main():
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
    for fileName in track(allFiles, description="Adding files..."):
        eventChain.Add(fileName)
        puppiJetChain.Add(fileName)
        triggerJetChain.Add(fileName)
        regionChain.Add(fileName)
    eventChain.AddFriend(puppiJetChain)
    eventChain.AddFriend(triggerJetChain)
    eventChain.AddFriend(regionChain)

    df = ROOT.RDataFrame(eventChain)

    console.print(f'Available columns: \n{df.GetColumnNames()}')


    numEvents = eventChain.GetEntries()
    console.print(f'Processing {numEvents} events...', style='underline')

    totalPuppiJets = 0
    totalTriggerJets = 0
    totalUnmatchedPuppiJets = 0
    totalUnmatchedTriggerJets = 0

    startIndex = random.randrange(0, numEvents-10000)

    eventTimes = []
    eventGrabTimes = []
    jetCreationTimes = []
    jetMatchingTimes = []

    for i in range(startIndex, startIndex+10000):
        # Grab the event
        start_time = perf_counter()
        eventChain.GetEntry(i)
        event_grab_time = perf_counter()
        eventGrabTimes.append(event_grab_time - start_time)

        # create the trigger and puppi jet objects
        triggerJets, puppiJets = createTriggerAndPuppiJets(eventChain)
        jetCreationTime = perf_counter()
        totalTriggerJets += len(triggerJets)
        totalPuppiJets += len(puppiJets)
        jetCreationTimes.append(jetCreationTime - event_grab_time)

        # Match the jets
        matchedJets, unmatchedTriggerJets, unmatchedPuppiJets = createMatchedAndUnmatchedJets(triggerJets, puppiJets)
        jetMatchingTime = perf_counter()
        totalUnmatchedPuppiJets+= len(unmatchedPuppiJets)
        totalUnmatchedTriggerJets+=len(unmatchedTriggerJets)
        jetMatchingTimes.append(jetMatchingTime-jetCreationTime)

        # Get the regions

        end_time = perf_counter()
        totalTime = end_time - start_time
        # console.print(f'Total event time {totalTime:.2f} seconds')
        eventTimes.append(totalTime)

    console.rule()
    console.print(f'Total trigger jets {totalTriggerJets}, total unmatched: {totalUnmatchedTriggerJets}, percent: {totalUnmatchedTriggerJets/totalTriggerJets:.2%}')
    console.print(f'Total Puppi jets {totalPuppiJets}, total unmatched: {totalUnmatchedPuppiJets}, percent: {totalUnmatchedPuppiJets/totalPuppiJets:.2%}')

    meanTime = statistics.mean(eventTimes)
    stdDev = statistics.pstdev(eventTimes)
    console.print(f'Mean time per event: {meanTime:.2} seconds, std-dev: {stdDev:.2f} seconds')
    predictedTotalTime = numEvents * meanTime
    predictedStdDev = math.sqrt(numEvents) * stdDev
    console.print(f'Projected total time in seconds: {predictedTotalTime:3g} seconds, projected std-dev: {predictedStdDev:3g}')

    meanEventGrabTime = statistics.mean(eventGrabTimes)
    stdEventGrabTime = statistics.pstdev(eventGrabTimes)
    console.print(f'Average event load time: {meanEventGrabTime}, std-dev: {stdEventGrabTime}')

    meanJetCreationTime = statistics.mean(jetCreationTimes)
    stdJetCreationTime = statistics.pstdev(jetCreationTimes)
    console.print(f'Average jet creation time: {meanJetCreationTime}, std-dev: {stdJetCreationTime}')

    meanJetMatchingTime = statistics.mean(jetMatchingTimes)
    stdJetMatchingTime = statistics.pstdev(jetMatchingTimes)
    console.print(f'Average jet matching time: {meanJetMatchingTime}, std-dev: {stdJetMatchingTime}')


if __name__ == '__main__':
    main()

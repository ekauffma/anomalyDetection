#mini+RAW actual data and MC Z to ee plot creation
import ROOT
from anomalyDetection.ZtoeePeakAnalysis.samples.RunC_mini_raw_sample import RunCSample
from anomalyDetection.ZtoeePeakAnalysis.samples.DY_mini_raw_sample import DYSample

from miniCICADAPeak import hasTwoElectrons, electronsPassCuts

import time
import math

def processSample(sampleName: str, theSample):
    twoElectronHist = ROOT.TH1F(
        f'{sampleName}_twoElectronHist',
        f'{sampleName}_twoElectronHist',
        25,
        70.0,
        120.0
    )
    twoElectronWCutHist = ROOT.TH1F(
        f'{sampleName}_twoElectronWCutHist',
        f'{sampleName}_twoElectronWCutHist',
        25,
        70.0,
        120.0
    )

    cicadaStep=0.5
    cicadaMin = 0.0
    cicadaMax = 10.0
    cicadaSteps = math.ceil((cicadaMax-cicadaMin)/cicadaStep)

    cicadaThresholds = [cicadaStep * x for x in range(cicadaSteps+1)]
    cicadaPlots = [
        ROOT.TH1F(f'{sampleName}_{threshold}_CICADAHist', f'{sampleName}_{threshold}_CICADAHist', 25, 70, 120) 
        for threshold in cicadaThresholds
    ]
    cicadaPlotDict = dict(zip(cicadaThresholds, cicadaPlots))

    numEntries = theSample.GetEntries()

    twoElectronEvents = 0.0
    twoGoodElectronEvents =  0.0

    properMassEvents = 0.0

    # prange = trange(
    #     numEntries,
    #     # 10000,
    #     dynamic_ncols=True,
    #     postfix=f'2e: {int(twoElectronEvents)}:{twoElectronEvents/numEntries:.2%}, 2ge: {int(twoGoodElectronEvents)}:{twoGoodElectronEvents/numEntries:.2%}'
    # )

    for entryNum in range(numEntries):
    # for entryNum in prange:
        # prange.set_postfix_str(f'2e: {int(twoElectronEvents)}:{twoElectronEvents/numEntries:.2%}, 2ge: {int(twoGoodElectronEvents)}:{twoGoodElectronEvents/numEntries:.2%}')
        theSample.GetEntry(entryNum)

        if hasTwoElectrons(theSample.ElectronInformation):
            twoElectronEvents += 1.0
            electronOneVector = ROOT.TLorentzVector()
            electronTwoVector = ROOT.TLorentzVector()

            electronOneVector.SetPtEtaPhiM(
                theSample.ElectronInformation.ptVector[0],
                theSample.ElectronInformation.etaVector[0],
                theSample.ElectronInformation.phiVector[0],
                theSample.ElectronInformation.massVector[0],
            )
            electronTwoVector.SetPtEtaPhiM(
                theSample.ElectronInformation.ptVector[1],
                theSample.ElectronInformation.etaVector[1],
                theSample.ElectronInformation.phiVector[1],
                theSample.ElectronInformation.massVector[1],            
            )

            invMass = (electronOneVector+electronTwoVector).M()
            # if invMass > 70.0 and invMass < 120.0:
            #     #print(invMass)
            #     #print(theSample.GetWeight())
            #     properMassEvents += 1.0
            #     if properMassEvents > 10000:
            #         break
            twoElectronHist.Fill(invMass, theSample.GetWeight())
            if invMass > 70.0 and invMass < 120.0:
                properMassEvents += 1.0
                if twoElectronHist.Integral() <= 0.0:
                    print("two electron hist integral borked")
                    print(f'entry num: {entryNum}')
                    print(f'proper mass events: {properMassEvents}')
                    break

            if electronsPassCuts(theSample.ElectronInformation):
                twoGoodElectronEvents+=1.0
                twoElectronWCutHist.Fill(invMass, theSample.GetWeight())

            for threshold in cicadaThresholds:
                if theSample.chain.anomalyScore >= threshold:
                    cicadaPlotDict[threshold].Fill(invMass, theSample.GetWeight())
    theFile = ROOT.TFile(f'{sampleName}_miniCICADAPeak.root','RECREATE')
    twoElectronHist.Write()
    twoElectronWCutHist.Write()
    for plot in cicadaPlots:
        plot.Write()
    theFile.Write()
    theFile.Close()
    print("Done!")

def main():
    samples = {
        'DY': DYSample,
        'RunC': RunCSample,
    }

    print('Starting CICADA peakfiding multiprocess')
    startTime = time.perf_counter()
    for key in samples:
        processSample(key, samples[key])
    endTime = time.perf_counter()
    print(f'Complete in {endTime-startTime:.2f} seconds')

if __name__ == '__main__':
    main()
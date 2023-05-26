#!/usr/bin/env python3
import ROOT
from unsupervisedZToeeHunt.proofOfConcept.samples.zeroBiasDSample import zeroBiasDSample
import time
from tqdm import trange
import math

print('Retrieved sample')

ROOT.gStyle.SetOptStat(0)

twoElectronCanvas = ROOT.TCanvas('twoElectronCanvas')
twoElectronWCutCanvas = ROOT.TCanvas('twoElectronsWCutCanvas')
cicadaEffectCanvas = ROOT.TCanvas('cicadaEffectCanvas')

twoElectronHist = ROOT.TH1F(
    'twoElectronHist',
    'twoElectronHist',
    25,
    70,
    120,
)
twoElectronWCutHist = ROOT.TH1F(
    'twoElectronWCutHist',
    'twoElectronWCutHist',
    25,
    70,
    120
)

cicadaStep = 0.1
cicadaMin = 0.0
cicadaMax = 7.0
cicadaSteps = math.ceil((cicadaMax-cicadaMin)/cicadaStep)

cicadaThresholds = [cicadaStep * x for x in range(cicadaSteps+1)]
cicadaPlots = [
    ROOT.TH1F(f'{threshold}_CICADAHist', f'{threshold}_CICADAHist', 25, 70, 120) for threshold in cicadaThresholds
]
cicadaPlotDict = dict(zip(cicadaThresholds, cicadaPlots))


startTime = time.perf_counter()
numEntries = zeroBiasDSample.GetEntries()
endTime = time.perf_counter()

print(f'Retrieved numEntries in : {endTime-startTime:4.2f} seconds')

def hasTwoElectrons(electronInfo):
    isGood = False
    if electronInfo.nElectrons == 2:
        isGood = True
    return isGood

def electronsPassCuts(electronInfo):
    isGood = False
    if electronInfo.chargeVector[0] * electronInfo.chargeVector[1] < 0 and electronInfo.ptVector[0] > 10 and electronInfo.ptVector[1] > 10:
        isGood = True
    return isGood

twoElectrons = 0
twoGoodElectrons = 0

for numEntry in trange(numEntries):
    zeroBiasDSample.GetEntry(numEntry)

    if hasTwoElectrons(zeroBiasDSample.electronChain):
        twoElectrons += 1
        electronOneVector = ROOT.TLorentzVector()
        electronTwoVector = ROOT.TLorentzVector()

        electronOneVector.SetPtEtaPhiM(
            zeroBiasDSample.electronChain.ptVector[0],
            zeroBiasDSample.electronChain.etaVector[0],
            zeroBiasDSample.electronChain.phiVector[0],
            zeroBiasDSample.electronChain.massVector[0]            
        )
        electronTwoVector.SetPtEtaPhiM(
            zeroBiasDSample.electronChain.ptVector[1],
            zeroBiasDSample.electronChain.etaVector[1],
            zeroBiasDSample.electronChain.phiVector[1],
            zeroBiasDSample.electronChain.massVector[1],            
        )

        invMass = (electronOneVector+electronTwoVector).M()
        twoElectronHist.Fill(invMass)

        if electronsPassCuts(zeroBiasDSample.electronChain):
            twoGoodElectrons += 1
            twoElectronWCutHist.Fill(invMass)

            for threshold in cicadaThresholds:
                if zeroBiasDSample.chain.anomalyScore >= threshold:
                    cicadaPlotDict[threshold].Fill(invMass)
twoElectronFraction = float(twoElectrons) / float(numEntries)
twoGoodElectronFraction = float(twoGoodElectrons) / float(numEntries)
print(f'two electrons: {twoElectronFraction:2.3%}')
print(f'two good electrons: {twoGoodElectronFraction:2.3%}')
twoElectronHist.SetMarkerStyle(20)
twoElectronWCutHist.SetMarkerStyle(20)
for threshold in cicadaThresholds:
    cicadaPlotDict[threshold].SetMarkerStyle(20)

def drawPreliminaryLatex():
    cmsLatex = ROOT.TLatex()
    cmsLatex.SetTextSize(0.06)
    cmsLatex.SetNDC()
    cmsLatex.SetTextAlign(11)
    cmsLatex.DrawLatex(0.1, 0.92, "#font[61]{CMS} #font[52]{Preliminary}")

def drawCICADAMessage(threshold):
    cicadaLatex = ROOT.TLatex()
    cicadaLatex.SetTextSize(0.06)
    cicadaLatex.SetNDC(True)
    cicadaLatex.SetTextSize(31)
    cicadaLatex.DrawLatex(0.9, 0.92, f'CICADA: {threshold: 2.2f}')

twoElectronCanvas.cd()
twoElectronHist.Draw('lpe1')
twoElectronHist.SetTitle('')
twoElectronHist.GetXaxis().SetTitle('Invariant Mass')
twoElectronHist.GetYaxis().SetTitle('Events')

drawPreliminaryLatex()

twoElectronLatex = ROOT.TLatex()
twoElectronLatex.SetTextSize(0.06)
twoElectronLatex.SetNDC(True)
twoElectronLatex.SetTextSize(31)
twoElectronLatex.DrawLatex(0.9, 0.92, 'Two Electrons')

twoElectronCanvas.Print('twoElectrons.png')

twoElectronWCutCanvas.cd()
twoElectronWCutHist.Draw('lpe1')
twoElectronWCutHist.SetTitle('')
twoElectronWCutHist.GetXaxis().SetTitle('Invariant Mass')
twoElectronWCutHist.GetYaxis().SetTitle('Events')

drawPreliminaryLatex()

twoElectronWCutLatex = ROOT.TLatex()
twoElectronWCutLatex.SetTextSize(0.06)
twoElectronWCutLatex.SetNDC(True)
twoElectronWCutLatex.SetTextSize(31)
twoElectronWCutLatex.DrawLatex(0.9, 0.92, 'Two Electrons W/ Cuts')

twoElectronWCutCanvas.Print('twoElectrons.png')

cicadaEffectCanvas.cd()
for threshold in cicadaThresholds:
    cicadaPlotDict[threshold].Draw('lpe1')
    cicadaPlotDict[threshold].SetTitle('')
    cicadaPlotDict[threshold].GetXaxis().SetTitle('Invariant Mass')
    cicadaPlotDict[threshold].GetYaxis().SetTitle('Events')

    drawPreliminaryLatex()

    drawCICADAMessage(threshold)
    #cicadaThresholdString = str(threshold).replace('.','p')
    cicadaThresholdString = f'{threshold:2.2f}'.replace('.','p')
    cicadaEffectCanvas.Print(f'electrons_cicada_{cicadaThresholdString}.png')
    cicadaEffectCanvas.Print('cicadaEffect.gif+50')
cicadaEffectCanvas.Print('cicadaEffect.gif++')

print('completed')
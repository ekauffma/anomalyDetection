import ROOT
import math

def getCombinedHistogram(fileDictionary: dict, histogramName:str, finalTag: str):
    keyList = list(fileDictionary.keys())
    firstKey = keyList[0]
    remainingKeys = keyList[1:]
    
    theHistogram = fileDictionary[firstKey].Get(f"{firstKey}_{histogramName}").Clone()
    theHistogram.SetNameTitle(f"{finalTag}_{histogramName}",f"{finalTag}_{histogramName}")

    for key in remainingKeys:
        theHistogram.Add(fileDictionary[key].Get(f"{key}_{histogramName}").Clone())
    
    return theHistogram

if __name__ == '__main__':
    DYFile = ROOT.TFile("DY_miniCICADAPeak.root")

    runs = ["RunA","RunB","RunC","RunD"]

    dataFiles = [
        ROOT.TFile(f"{run}_miniCICADAPeak.root")
        for run in runs
    ]

    runFileDict = dict(zip(runs, dataFiles))

    def drawPreliminaryLatex():
        cmsLatex = ROOT.TLatex()
        cmsLatex.SetTextSize(0.06)
        cmsLatex.SetNDC()
        cmsLatex.SetTextAlign(11)
        cmsLatex.DrawLatex(0.1, 0.92, "#font[61]{CMS} #font[52]{Preliminary}")

    #
    # Two electron plot
    # 

    DYtwoElectrons = DYFile.Get("DY_twoElectronHist")
    dataTwoElectrons = getCombinedHistogram(fileDictionary=runFileDict,histogramName="twoElectronHist",finalTag="Data")

    rescaledDYtwoElectrons = DYtwoElectrons.Clone()
    rescaledDYtwoElectrons.Scale(dataTwoElectrons.Integral()/rescaledDYtwoElectrons.Integral())

    twoElectronCanvas = ROOT.TCanvas("twoElectronCanvas")

    dataTwoElectrons.SetMarkerStyle(20)
    dataTwoElectrons.SetMarkerColor(ROOT.kBlack)
    dataTwoElectrons.SetLineColor(ROOT.kBlack)
    rescaledDYtwoElectrons.SetLineColor(ROOT.kBlack)
    rescaledDYtwoElectrons.SetLineWidth(0)
    rescaledDYtwoElectrons.SetFillColor(ROOT.kBlue)

    rescaledDYtwoElectrons.Draw('HIST')
    rescaledDYtwoElectrons.SetTitle('')
    rescaledDYtwoElectrons.GetXaxis().SetTitle('Invariant Mass')
    rescaledDYtwoElectrons.GetYaxis().SetTitle('Events')
    dataTwoElectrons.Draw('lpe1 SAME')    

    drawPreliminaryLatex()
    twoElectronLatex = ROOT.TLatex()
    twoElectronLatex.SetTextSize(0.06)
    twoElectronLatex.SetNDC(True)
    #twoElectronLatex.SetTextSize(31) #?
    twoElectronLatex.SetTextAlign(31)
    twoElectronLatex.DrawLatex(0.9, 0.92, "Two Electrons")

    twoElectronCanvas.Print("twoElectrons.png")

    # 
    # Two electron with cuts plot
    # 

    DYtwoElectronsWCut = DYFile.Get("DY_twoElectronWCutHist")
    dataTwoElectronsWCut = getCombinedHistogram(fileDictionary=runFileDict,histogramName="twoElectronWCutHist",finalTag="Data")

    rescaledDYtwoElectronsWCut = DYtwoElectronsWCut.Clone()
    rescaledDYtwoElectronsWCut.Scale(dataTwoElectronsWCut.Integral()/rescaledDYtwoElectronsWCut.Integral())

    twoElectronWCutCanvas = ROOT.TCanvas("twoElectronWCutCanvas")

    dataTwoElectronsWCut.SetMarkerStyle(20)
    dataTwoElectronsWCut.SetMarkerColor(ROOT.kBlack)
    dataTwoElectronsWCut.SetLineColor(ROOT.kBlack)
    rescaledDYtwoElectronsWCut.SetLineColor(ROOT.kBlack)
    rescaledDYtwoElectronsWCut.SetLineWidth(0)
    rescaledDYtwoElectronsWCut.SetFillColor(ROOT.kBlue)

    rescaledDYtwoElectronsWCut.Draw('HIST')
    rescaledDYtwoElectronsWCut.SetTitle('')
    rescaledDYtwoElectronsWCut.GetXaxis().SetTitle('Invariant Mass')
    rescaledDYtwoElectronsWCut.GetYaxis().SetTitle('Events')
    dataTwoElectronsWCut.Draw('lpe1 SAME')    

    drawPreliminaryLatex()
    twoElectronLatex = ROOT.TLatex()
    twoElectronLatex.SetTextSize(0.06)
    twoElectronLatex.SetNDC(True)
    #twoElectronLatex.SetTextSize(31) #?
    twoElectronLatex.SetTextAlign(31)
    twoElectronLatex.DrawLatex(0.9, 0.92, "Two Electrons W/ Cuts")

    twoElectronWCutCanvas.Print("twoElectronsWCut.png")

    # 
    # CICADA effect plots
    # 

    cicadaStep=0.5
    cicadaMin = 0.0
    cicadaMax = 50.0
    cicadaSteps = math.ceil((cicadaMax-cicadaMin)/cicadaStep)

    cicadaThresholds = [cicadaStep * x for x in range(cicadaSteps+1)]

    cicadaEffectCanvas = ROOT.TCanvas("cicadaEffectCanvas")

    def drawCICADAMessage(threshold):
        cicadaLatex = ROOT.TLatex()
        cicadaLatex.SetTextSize(0.05)
        cicadaLatex.SetNDC(True)
        cicadaLatex.SetTextAlign(31)
        cicadaLatex.DrawLatex(0.9, 0.92, '#font[42]{59.7 fb^{-1}, 13TeV} #font[52]{miniCICADA: '+f'{threshold}'+'}')

    for threshold in cicadaThresholds:
        DYPlot = DYFile.Get(f"DY_{threshold}_CICADAHist")
        dataPlot = getCombinedHistogram(
            fileDictionary=runFileDict,
            histogramName=f"{threshold}_CICADAHist",
            finalTag="Data",
        )

        rescaledDYPlot = DYPlot.Clone()
        rescaledDYPlot.Scale(dataPlot.Integral()/rescaledDYPlot.Integral())

        dataPlot.SetMarkerStyle(20)
        dataPlot.SetMarkerColor(ROOT.kBlack)
        dataPlot.SetLineColor(ROOT.kBlack)
        rescaledDYPlot.SetLineColor(ROOT.kBlack)
        rescaledDYPlot.SetLineWidth(0)
        rescaledDYPlot.SetFillColor(ROOT.kBlue)

        rescaledDYPlot.Draw('HIST')
        rescaledDYPlot.SetTitle('')
        rescaledDYPlot.GetXaxis().SetTitle('Invariant Mass')
        rescaledDYPlot.GetYaxis().SetTitle('Events')
        dataPlot.Draw('lpe1 SAME')

        drawPreliminaryLatex()
        drawCICADAMessage(threshold)
        
        cicadaThresholdString = f'{threshold}'.replace('.','p')
        cicadaEffectCanvas.Print(f"twoelectrons_wcut_cicada_{cicadaThresholdString}.png")
        cicadaEffectCanvas.Print('cicadaEffect.gif+50')
    cicadaEffectCanvas.Print('cicadaEffect.gif++')



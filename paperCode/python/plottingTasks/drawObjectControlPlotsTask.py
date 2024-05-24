# !/usr/bin/env python3
from pathlib import Path
from anomalyDetection.paperCode.plottingCore.plotTask import drawPlotTask
import ROOT
from anomalyDetection.anomalyTriggerSkunkworks.utilities.decorators import quietROOTFunc

class drawObjectControlPlotsTask(drawPlotTask):
    def __init__(
            self,
            taskName: str,
            dictOfFiles: list,
            outputPath: Path = Path('/nfs_scratch/aloeliger/PaperPlotFiles/FinalizedPlots/CICADA_Object_Controls/')
    ):
        super().__init__(taskName, dictOfFiles, outputPath)

    def parseHistogramName(self, histogramName):
        splitName = histogramName.split('_xxx_')
        sampleName, variable = splitName[0], splitName[1]
        return sampleName, variable

    def drawControl(self, plot, sample, variable):
        canvasName = f'{sample}_xxx_{variable}_xxx_control'
        theCanvas = ROOT.TCanvas(canvasName)
        
        nBins = plot.GetNbinsX()

        try:
            plot.Scale(1.0/plot.Integral(0, nBins+1))
        except ZeroDivisionError:
            pass

        plot.SetMarkerStyle(20)
        plot.SetMarkerColor(ROOT.kBlack)
        plot.SetLineColor(ROOT.kBlack)

        plot.Draw("EP X0")
        plot.GetYaxis().SetTitle("Fraction of Events")
        plot.GetXaxis().SetTitle(variable)

        quietROOTFunc(theCanvas.SaveAs)(
            str(
                self.outputPath/f'{canvasName}.png'
            )
        )

    def drawPlots(self):
        ROOT.gStyle.SetOptStat(0)
        objectFiles = self.dictOfFiles['controls']
        theFile = ROOT.TFile(objectFiles)

        listOfKeys = list(theFile.GetListOfKeys())
        listOfKeys = [x.GetName() for x in listOfKeys]

        plots = {}
        for key in listOfKeys:
            sampleName, variable = self.parseHistogramName(key)
            if sampleName not in plots:
                plots[sampleName] = {}
            if variable not in plots[sampleName]:
                plots[sampleName][variable] = theFile.Get(key).Clone()

        for sample in plots:
            for variable in plots[sample]:
                self.drawControl(plots[sample][variable], sample, variable)

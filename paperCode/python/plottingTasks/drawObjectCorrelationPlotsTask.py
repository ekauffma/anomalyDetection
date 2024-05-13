# !/usr/bin/env python3

from pathlib import Path
from anomalyDetection.paperCode.plottingCore.plotTask import drawPlotTask
import ROOT
from anomalyDetection.anomalyTriggerSkunkworks.utilities.decorators import quietROOTFunc

class drawObjectCorrelationPlotsTask(drawPlotTask):
    def __init__(
            self,
            taskName: str,
            dictOfFiles: list,
            outputPath: Path = Path('/nfs_scratch/aloeliger/PaperPlotFiles/FinalizedPlots/CICADA_Object_Correlations/')
    ):
        super().__init__(taskName, dictOfFiles, outputPath)

    def parseHistogramName(self, histogramName):
        splitName = histogramName.split('_xxx_')
        sampleName, score, variable = splitName[0], splitName[1], splitName[2]
        return sampleName, score, variable

    #TODO: Re-use the code on these from another place where we have this defined
    def columnNormalizeHistogram(self, histogram):
        histogramName = f'{histogram.GetName()}_column_norm'
        columnNormHisto = histogram.Clone()
        columnNormHisto.SetNameTitle(
            histogramName,
            histogramName,
        )
        
        nbins_x = columnNormHisto.GetNbinsX()
        nbins_y = columnNormHisto.GetNbinsY()
        
        for xBin in range(1, nbins_x+1):
            totalContent = 0.0
            for yBin in range(1, nbins_y+1):
                totalContent += columnNormHisto.GetBinContent(xBin, yBin)
            if totalContent != 0.0:
                for yBin in range(1, nbins_y+1):
                    content = columnNormHisto.GetBinContent(xBin, yBin)
                    columnNormHisto.SetBinContent(xBin, yBin, content/totalContent)
        return columnNormHisto

    def rowNormalizeHistogram(self, histogram):
        histogramName = f"{histogram.GetName()}_row_norm"
        rowNormHisto = histogram.Clone()
        rowNormHisto.SetNameTitle(
            histogramName,
            histogramName,
        )
        
        nbins_x = rowNormHisto.GetNbinsX()
        nbins_y = rowNormHisto.GetNbinsY()
        
        for yBin in range(1, nbins_y+1):
            totalContent = 0.0
            for xBin in range(1, nbins_x+1):
                totalContent += rowNormHisto.GetBinContent(xBin, yBin)
            if totalContent != 0.0:
                for xBin in range(1, nbins_x+1):
                    content = rowNormHisto.GetBinContent(xBin, yBin)
                    rowNormHisto.SetBinContent(xBin, yBin, content/totalContent)
        return rowNormHisto


    def draw2DCorrelationHistogram(self, correlationHisto, score, sample, variable, extraTag=""):
        canvasName = f'{sample}_xxx_{score}_xxx_{variable}'
        if extraTag != "":
            canvasName = f'{sample}_xxx_{score}_xxx_{variable}_xxx_{extraTag}'
        theCanvas = ROOT.TCanvas(canvasName)

        correlationHisto.Draw("COLZ")
        correlationHisto.GetYaxis().SetTitle(variable)
        correlationHisto.GetXaxis().SetTitle(score)

        quietROOTFunc(theCanvas.SaveAs)(
            str(
                self.outputPath / f'{canvasName}.png'
            )
        )

    def drawPlots(self):
        ROOT.gStyle.SetOptStat(0)
        objectsFile = self.dictOfFiles['objects']
        theFile = ROOT.TFile(objectsFile)

        listOfKeys = list(theFile.GetListOfKeys())
        listOfKeys = [x.GetName() for x in listOfKeys]

        plots = {}
        for key in listOfKeys:
            sampleName, score, variable = self.parseHistogramName(key)
            if score not in plots:
                plots[score] = {}
            if sampleName not in plots[score]:
                plots[score][sampleName] = {}
            if variable not in plots[score][sampleName]:
                plots[score][sampleName][variable] = theFile.Get(key).Clone()

        for score in plots:
            for sampleName in plots[score]:
                for variable in plots[score][sampleName]:
                    theHisto = plots[score][sampleName][variable]
                    self.draw2DCorrelationHistogram(
                        theHisto,
                        score,
                        sampleName,
                        variable,
                    )
                    self.draw2DCorrelationHistogram(
                        self.columnNormalizeHistogram(theHisto),
                        score,
                        sampleName,
                        variable,
                        extraTag="column_norm",
                    )
                    self.draw2DCorrelationHistogram(
                        self.rowNormalizeHistogram(theHisto),
                        score,
                        sampleName,
                        variable,
                        extraTag="row_norm",
                    )

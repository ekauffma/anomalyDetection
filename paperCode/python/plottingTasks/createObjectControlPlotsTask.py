from anomalyDetection.paperCode.plottingCore.plotTask import createPlotTask

import ROOT
from anomalyDetection.paperCode.plottingUtilities.models import *
from pathlib import Path

class createObjectControlPlotsTask(createPlotTask):
    def __init__(
            self,
            taskName: str,
            outputFileName: str,
            dictOfSamples: dict,
            outputPath: Path = Path("/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/"),
            nBins: int = 30,
    ):
        super().__init__(
            taskName,
            outputFileName,
            dictOfSamples,
            outputPath,
        )

        self.nBins = nBins

    def makeBooking(self, dataframe, sample, variable, variableMax, variableMin):
        histoName = f'{sample}_xxx_{variable}'
        histoModel = ROOT.RDF.TH1DModel(
            histoName,
            histoName,
            self.nBins,
            variableMin,
            variableMax,
        )
        return dataframe.Histo1D(histoModel, variable)

    def createPlots(self):
        #okay, we need a list of object variables that we are creating the plots for
        objectVariables = [
            'HT',
        
            'nEGs',
            'egEt',
            'egPhi',
            'egEta',

            'nTaus',
            'tauEt',
            'tauPhi',
            'tauEta',

            'nJets',
            'jetEt',
            'jetPhi',
            'jetEta',

            'nMuons',
            'muonEt',
            'muonPhi',
            'muonEta',
        ]
        
        #print("data frames")
        dictOfDataframes = {}
        for sampleName in self.dictOfSamples:
            dictOfDataframes[sampleName] = self.dictOfSamples[sampleName].getNewDataframe()
            dictOfDataframes[sampleName] = toyHTModel.applyFrameDefinitions(dictOfDataframes[sampleName])
        
        #print("Maxes")
        variableMaxes, variableMins = self.getVariableMaxAndMins(objectVariables, dictOfDataframes)

        #print("Bookings")
        for sample in dictOfDataframes:
            for variable in objectVariables:
                self.plotsToBeWritten.append(
                    self.makeBooking(
                        dictOfDataframes[sample],
                        sample,
                        variable,
                        variableMaxes[variable],
                        variableMins[variable],
                    )
                )
        #print("Done")
        
    def getVariableMaxAndMins(self, variables, sampleDataframes):
        sampleMaxes = {}
        sampleMins = {}
        # book all the calculations up front
        #print("Bookings")
        for sample in sampleDataframes:
            #print(sample)
            sampleDataframe = sampleDataframes[sample]
            sampleMaxes[sample] = {}
            sampleMins[sample] = {}
            for variable in variables:
                #print(variable)
                sampleMaxes[sample][variable] = sampleDataframe.Max(variable)
                sampleMins[sample][variable] = sampleDataframe.Min(variable)
        #trigger the actual calculation after all are booked
        #print("Trigger")
        for sample in sampleDataframes:
            for variable in variables:
                sampleMaxes[sample][variable] = sampleMaxes[sample][variable].GetValue()
                sampleMins[sample][variable] = sampleMins[sample][variable].GetValue()

        #now let's get the overall maxes
        #print("Overall")
        variableMaxes = {}
        variableMins = {}
        for variable in variables:
            possibleMaxes = []
            possibleMins = []
            for sample in sampleDataframes:
                possibleMaxes.append(sampleMaxes[sample][variable])
                possibleMins.append(sampleMins[sample][variable])
            variableMaxes[variable] = max(possibleMaxes)
            variableMins[variable] = min(possibleMins)
        return variableMaxes, variableMins

import ROOT
import argparse
from anomalyDetection.paperCode.samples.paperSampleBuilder import samples
from rich.console import Console
import os

console = Console()

def makePlotsForScores(theDataframe, listOfScores, baseName):
    resultPlots = []
    for scoreName in listOfScores:
        minScore = 0.0
        maxScore = 256.0 # actually 255.99609375
        histName = f'{baseName}_{scoreName}_hist'
        theModel = ROOT.RDF.TH1DModel(
            histName,
            histName,
            100,
            minScore,
            maxScore
        )

        resultPlots.append(theDataframe.Histo1D(theModel, scoreName))
    return resultPlots

def main(args):
    # start this nonsense by grabbing all the possible samples, and separate out the data
    mcSampleNames = list(samples.keys())
    try:
        mcSampleNames.remove('ZeroBias')
    except ValueError:
        console.log("Failed to find Zero Bias in list of samples and prune it out. Check the samples.", style='red')
        exit(1)
    # Now, let's get the data sample, and prepare even/odd lumi dataframes
    # even lumi: training
    # odd lumi: test
    zeroBiasDataframe = samples['ZeroBias'].getNewDataframe()
    evenLumiZBDataframe = zeroBiasDataframe.Filter('lumi % 2 == 0')
    oddLumiZBDataframe = zeroBiasDataframe.Filter('lumi % 2 == 1')

    scoreNames = [
        'CICADA_v1p2p0_score',
        'CICADA_v2p2p0_score',
        'CICADA_v1p2p0N_score',
        'CICADA_v2p2p0N_score',
    ]
    allPlots = []

    allPlots += makePlotsForScores(evenLumiZBDataframe, scoreNames, 'Train_ZeroBias')
    allPlots += makePlotsForScores(oddLumiZBDataframe, scoreNames, 'Test_ZeroBias')
    console.log(f'Zero Bias: {len(samples["ZeroBias"].listOfFiles):>6d} Files')

    mcDataframes = []
    with console.status("Running through samples..."):
        for sampleName in mcSampleNames:
            theDataframe = samples[sampleName].getNewDataframe()
            console.log(f'{sampleName}: {len(samples[sampleName].listOfFiles):>6d} Files')
            allPlots += makePlotsForScores(
                theDataframe,
                scoreNames,
                sampleName,
            )
            mcDataframes.append(theDataframe)
    console.log('[bold green]\[Done][/bold green] Logging all plots to be made.')
    # set-up an output location for all the plots that this is going to 
    plotOutputLocation = '/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/'
    os.makedirs(plotOutputLocation, exist_ok=True)
    outputFileName = os.path.join(plotOutputLocation, 'scorePlots.root')
    theOutputFile = ROOT.TFile(outputFileName, 'RECREATE')
    with console.status('Writing plot file...'):
        for plot in allPlots:
            plot.Write()
        theOutputFile.Write()
        theOutputFile.Close()
    console.log(f'[bold green]\[Done][/bold green] Writing files')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create score plots from the paper samples")

    args = parser.parse_args()
    
    main(args)

import ROOT
import argparse
from anomalyDetection.paperCode.samples.paperSampleBuilder import samples
from rich.console import Console
import os

console = Console()

def makePlotsForScores(theDataframe, listOfScores, baseName, nBins=100):
    resultPlots = []
    for scoreName in listOfScores:
        minScore = 0.0
        if scoreName != 'HT':
            maxScore = 256.0 # actually 255.99609375
        else:
            maxScore = 1024.0
        histName = f'{baseName}_{scoreName}_hist'
        theModel = ROOT.RDF.TH1DModel(
            histName,
            histName,
            nBins,
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
    #function for calculating HT
    HTFunction = """
    try {
       for(int i = 0; i < L1Upgrade.sumType.size(); ++i){
          if(L1Upgrade.sumType.at(i) == 1 and L1Upgrade.sumBx.at(i) == 0){
             return (double) L1Upgrade.sumEt.at(i);
          }
       }
       return 0.0;
    }
    catch (const std::runtime_error& e) {
       return 0.0;
    }
    """

    # Now, let's get the data sample, and prepare even/odd lumi dataframes
    # even lumi: training
    # odd lumi: test
    zeroBiasDataframe = samples['ZeroBias'].getNewDataframe()
    zeroBiasDataframe = zeroBiasDataframe.Define("HT", HTFunction)
    evenLumiZBDataframe = zeroBiasDataframe.Filter('lumi % 2 == 0')
    oddLumiZBDataframe = zeroBiasDataframe.Filter('lumi % 2 == 1')

    scoreNames = [
        'CICADA_v1p2p0_score',
        'CICADA_v2p2p0_score',
        'CICADA_v1p2p0N_score',
        'CICADA_v2p2p0N_score',
        'HT'
    ]
    allPlots = []

    allPlots += makePlotsForScores(evenLumiZBDataframe, scoreNames, 'Train_ZeroBias')
    allPlots += makePlotsForScores(oddLumiZBDataframe, scoreNames, 'Test_ZeroBias')
    console.log(f'Zero Bias: {len(samples["ZeroBias"].listOfFiles):>6d} Files')

    if args.ForROCs:
        nBinsForPlots = 100000
    else:
        nBinsForPlots = 100

    mcDataframes = []
    with console.status("Running through samples..."):
        for sampleName in mcSampleNames:
            theDataframe = samples[sampleName].getNewDataframe()
            console.log(f'{sampleName}: {len(samples[sampleName].listOfFiles):>6d} Files')
            theDataframe = theDataframe.Define('HT', HTFunction)
            allPlots += makePlotsForScores(
                theDataframe,
                scoreNames,
                sampleName,
                nBins = nBinsForPlots,
            )
            mcDataframes.append(theDataframe)
    console.log('[bold green]\[Done][/bold green] Logging all plots to be made.')

    # set-up an output location for all the plots that this is going to 
    plotOutputLocation = '/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/'
    os.makedirs(plotOutputLocation, exist_ok=True)
    if args.ForROCs:
        outputFileName = 'scorePlotsForROCs.root'
    else:
        outputFileName = 'scorePlots.root'
    outputFileName = os.path.join(plotOutputLocation, outputFileName)
    theOutputFile = ROOT.TFile(outputFileName, 'RECREATE')
    with console.status('Writing plot file...'):
        for plot in allPlots:
            plot.Write()
        theOutputFile.Write()
        theOutputFile.Close()
    console.log(f'[bold green]\[Done][/bold green] Writing files')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create score plots from the paper samples")

    parser.add_argument(
        "--ForROCs",
        action="store_true",
        help="create score plots to be used in a ROC calculation, which changes binning and score location",
    )

    args = parser.parse_args()
    
    main(args)

import ROOT
import argparse
from anomalyDetection.paperCode.samples.paperSampleBuilder import reducedSamples as samples
from rich.console import Console
from pathlib import Path

console = Console()

def makeCICADAScoreHTPlots(theDataframe, listOfScores, sampleName, nBins=100):
    resultPlots = []
    for scoreName in listOfScores:
        histoName = f'{sampleName}_{scoreName}_HT'
        histoModel = ROOT.RDF.TH2DModel(
            histoName,
            histoName,
            100,
            0.0,
            256.0,
            100,
            0.0,
            1024.0
        )
        thePlot = theDataframe.Histo2D(
            histoModel,
            scoreName,
            "HT",
        )
        resultPlots.append(thePlot)
    return resultPlots

def main(args):
    sampleNames = list(samples.keys())
    
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

    scoreNames = [
        'CICADA_v1p2p0_score',
        'CICADA_v2p2p0_score',
        'CICADA_vXp2p0_teacher_score',

        'CICADA_v1p2p0N_score',
        'CICADA_v2p2p0N_score',
        'CICADA_vXp2p0N_teacher_score',
        
        'CICADA_v1p2p1_score',
        'CICADA_v2p2p1_score',
        'CICADA_vXp2p1_teacher_score',

        'CICADA_v1p2p1N_score',
        'CICADA_v2p2p1N_score',
        'CICADA_vXp2p1N_teacher_score',

        'CICADA_v1p2p2_score',
        'CICADA_v2p2p2_score',
        'CICADA_vXp2p2_teacher_score',

        'CICADA_v1p2p2N_score',
        'CICADA_v2p2p2N_score',
        'CICADA_vXp2p2N_teacher_score',

        'GADGET_v1p0p0_Teacher_score',
        'GADGET_v1p0p0_score',

        'CICADA_v2p1p2',
    ]    

    #
    # Fails on  too many files
    #
    # allPlots = []
    # with console.status("Running through samples..."):
    #     for sampleName in sampleNames:
    #         theDataframe = samples[sampleName].getNewDataframe()
    #         theDataframe = theDataframe.Define('HT', HTFunction)
    #         allPlots += makeCICADAScoreHTPlots(
    #             theDataframe,
    #             scoreNames,
    #             sampleName,
    #         )
    # plotOutputLocation = '/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/'
    # os.makedirs(plotOutputLocation, exist_ok=True)
    # outputFileName = 'CICADA_HT_Correlation.root'
    # outputFileName = os.path.join(plotOutputLocation, outputFileName)
    # theOutputFile = ROOT.TFile(outputFileName, 'RECREATE')
    # with console.status('Writing plot file...'):
    #     for index, plot in enumerate(allPlots):
    #         console.log(f'Plot {index:>4d}...')
    #         plot.Write()
    #     theOutputFile.Write()
    #     theOutputFile.Close()
    # console.log("Done!", style="bold green")
    plotOutputLocation = Path('/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/')
    plotOutputLocation.mkdir(parents=True, exist_ok=True)
    outputPath = plotOutputLocation / 'CICADA_HT_Correlation.root'
    theOutputFile = ROOT.TFile(str(outputPath), 'RECREATE')
    
    for sampleName in sampleNames:
        console.log(f'{sampleName}: {len(samples[sampleName].listOfFiles):>6d} Files')
        theDataframe = samples[sampleName].getNewDataframe()
        theDataframe = theDataframe.Define('HT', HTFunction)
        
        plots = makeCICADAScoreHTPlots(
            theDataframe,
            scoreNames,
            sampleName,
        )
        for plot in plots:
            plot.Write()
        del theDataframe
    theOutputFile.Write()
    theOutputFile.Close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create plots examining the CICADA/HT correlation")

    args = parser.parse_args()

    main(args)

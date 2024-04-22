import ROOT
import os
from rich.console import Console
from rich.progress import track
import numpy as np
import re
import argparse
from anomalyDetection.anomalyTriggerSkunkworks.utilities.decorators import quietROOTFunc

console = Console()

def main(args):
    ROOT.gStyle.SetOptStat(0)
    console.log("CICADA HT Correlation")

    basePath = '/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/'
    theFile = ROOT.TFile(
        os.path.join(basePath, 'CICADA_HT_Correlation.root')
    )

    outputDirectory = '/nfs_scratch/aloeliger/PaperPlotFiles/FinalizedPlots/HTCorrelation/'
    os.makedirs(outputDirectory, exist_ok=True)

    listOfKeys = list(theFile.GetListOfKeys())
    listOfKeys = [x.GetName() for x in listOfKeys]

    scoreNames = [
        'CICADA_v1p2p0_score_HT',
        'CICADA_v2p2p0_score_HT',
        'CICADA_vXp2p0_teacher_score_HT',

        'CICADA_v1p2p0N_score_HT',
        'CICADA_v2p2p0N_score_HT',
        'CICADA_vXp2p0N_teacher_score_HT',
        
        'CICADA_v1p2p1_score_HT',
        'CICADA_v2p2p1_score_HT',
        'CICADA_vXp2p1_teacher_score_HT',

        'CICADA_v1p2p1N_score_HT',
        'CICADA_v2p2p1N_score_HT',
        'CICADA_vXp2p1N_teacher_score_HT',

        'CICADA_v1p2p2_score_HT',
        'CICADA_v2p2p2_score_HT',
        'CICADA_vXp2p2_teacher_score_HT',

        'CICADA_v1p2p2N_score_HT',
        'CICADA_v2p2p2N_score_HT',
        'CICADA_vXp2p2N_teacher_score_HT',

        'GADGET_v1p0p0_Teacher_score_HT',
        'GADGET_v1p0p0_score_HT',

        'CICADA_v2p1p2_HT',
    ]
    
    samplePattern = re.compile('.*(?=_(CICADA|GADGET|HT_HT))')
    def sample_matched_substring(s):
        match = samplePattern.search(s)
        return match.group(0) if match else None
    vectorizedSampleNames = np.vectorize(sample_matched_substring, otypes=[object])
    sampleNames = vectorizedSampleNames(listOfKeys)
    sampleNames = list(np.unique(sampleNames))
    console.print(sampleNames)

    for score in scoreNames:
        for sampleName in sampleNames:
            console.log(f'Sample: {sampleName:50}, score: {score:20}')
            plotName = f'{sampleName}_{score}'
            #console.log(plotName)
            thePlot = theFile.Get(plotName)
            canvasName = f'{sampleName}_{score}_correlation'
            theCanvas = ROOT.TCanvas(canvasName, canvasName)

            thePlot.Draw("COLZ")

            axisNameMap = {
                'CICADA_v1p2p0_score_HT': 'CICADA v1.2.0',
                'CICADA_v2p2p0_score_HT': 'CICADA v2.2.0',
                'CICADA_vXp2p0_teacher_score_HT': 'CICADA vX.2.0 Teacher',

                'CICADA_v1p2p0N_score_HT': 'CICADA v1.2.0N',
                'CICADA_v2p2p0N_score_HT': 'CICADA v2.2.0N',
                'CICADA_vXp2p0N_teacher_score_HT': 'CICADA vX.2.0N Teacher',
                
                'CICADA_v1p2p1_score_HT': 'CICADA v1.2.1',
                'CICADA_v2p2p1_score_HT': 'CICADA v2.2.1',
                'CICADA_vXp2p1_teacher_score_HT': 'CICADA vX.2.1 Teacher',

                'CICADA_v1p2p1N_score_HT': 'CICADA v1.2.1N',
                'CICADA_v2p2p1N_score_HT': 'CICADA v2.2.1N',
                'CICADA_vXp2p1N_teacher_score_HT': 'CICADA vX.2.1N Teacher',

                'CICADA_v1p2p2_score_HT': 'CICADA v1.2.2',
                'CICADA_v2p2p2_score_HT': 'CICADA v2.2.2',
                'CICADA_vXp2p2_teacher_score_HT': 'CICADA vX.2.2 Teacher',

                'CICADA_v1p2p2N_score_HT': 'CICADA v1.2.2N',
                'CICADA_v2p2p2N_score_HT': 'CICADA v2.2.2N',
                'CICADA_vXp2p2N_teacher_score_HT': 'CICADA vX.2.2N Teacher',

                'GADGET_v1p0p0_Teacher_score_HT': 'GADGET Teacher v1.0.0',
                'GADGET_v1p0p0_score_HT': 'GADGET v1.0.0',

                'CICADA_v2p1p2_HT':'CICADA v2.1.2',
            }

            thePlot.GetYaxis().SetTitle("HT")
            thePlot.GetXaxis().SetTitle(axisNameMap[score])
            
            quietROOTFunc(theCanvas.SaveAs)(
                os.path.join(outputDirectory, f'{canvasName}.png')
            )
    theFile.Close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    args = parser.parse_args()
    
    main(args)

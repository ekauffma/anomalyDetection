import ROOT
import argparse
from rich.console import Console
from rich.progress import track
import os
import numpy as np
import re
from anomalyDetection.anomalyTriggerSkunkworks.utilities.decorators import quietROOTFunc

console = Console()

def main(args):
    ROOT.gStyle.SetOptStat(0)

    basePath = '/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/'
    theFile = ROOT.TFile(
        os.path.join(basePath, 'scorePlots.root')
    )

    outputDirectory = '/nfs_scratch/aloeliger/PaperPlotFiles/FinalizedPlots/ScorePlots/'
    os.makedirs(outputDirectory, exist_ok=True)
    
    listOfKeys = list(theFile.GetListOfKeys())
    listOfKeys = [x.GetName() for x in listOfKeys]
    
    #console.print(listOfKeys)
    #We need to get a list of the available samples and score hist variables
    scoreNamePattern = re.compile('(anomalyScore|CICADA|HT_).*hist(?=$)')
    def score_matched_substring(s):
        match = scoreNamePattern.search(s)
        return match.group(0) if match else None
    vectorizedScoreNames = np.vectorize(score_matched_substring,  otypes=[object])
    scoreNames = vectorizedScoreNames(listOfKeys)
    #console.print(scoreNames)
    scoreNames = list(np.unique(scoreNames))
    console.print(scoreNames)

    samplePattern = re.compile('.*(?=_(anomalyScore|CICADA|HT))')
    def sample_matched_substring(s):
        match = samplePattern.search(s)
        return match.group(0) if match else None
    vectorizedSampleNames = np.vectorize(sample_matched_substring, otypes=[object])
    sampleNames = vectorizedSampleNames(listOfKeys)
    sampleNames = list(np.unique(sampleNames))
    console.print(sampleNames)
    
    try:
        sampleNames.remove('Train_ZeroBias')
    except ValueError:
        console.log(f'Failed to find Train_ZeroBias in the list of samples', style='red')
        exit(1)

    try:
        sampleNames.remove('Test_ZeroBias')
    except ValueError:
        console.log(f'Failed to find Test_ZeroBias in the list of samples', style='red')
        exit(1)

    try:
        sampleNames.remove('SingleNeutrino_E-10-gun')
    except ValueError:
        console.log(f'Failed to find SingleNeutrino_E-10-gun in the list of samples', style='red')
        exit(1)

    # Okay, for each score that we have, let's pull the train and test zerobias samples out
    # We will color train blue, and test red
    # for each sample then, we will make a plot with these two scores
    #the sample will be green

    for score in scoreNames:
        TrainZeroBias = theFile.Get(f'Train_ZeroBias_{score}')
        TestZeroBias = theFile.Get(f'Test_ZeroBias_{score}')
        SingleNeutrino = theFile.Get(f'SingleNeutrino_E-10-gun_{score}')
        
        TrainZeroBias.Scale(1.0/TrainZeroBias.Integral())
        TestZeroBias.Scale(1.0/TestZeroBias.Integral())
        SingleNeutrino.Scale(1.0/SingleNeutrino.Integral())

        TrainZeroBias.SetLineWidth(4)
        TestZeroBias.SetLineWidth(4)
        SingleNeutrino.SetLineWidth(4)
        
        TrainZeroBias.SetLineColor(ROOT.kBlue)
        TestZeroBias.SetLineColor(ROOT.kRed)
        SingleNeutrino.SetLineColor(ROOT.kOrange)

        TrainZeroBias.SetTitle("")

        for sampleName in track(sampleNames, description="Saving samples"):
            sample = theFile.Get(f'{sampleName}_{score}')
            
            sample.SetLineWidth(4)
            sample.SetLineColor(ROOT.kGreen)
            try:
                sample.Scale(1.0/sample.Integral())
            except ZeroDivisionError:
                sample.Scale(0.0)
                console.log(f"Got a zero division for score: {score} and sample: {sampleName}")

            theCanvas = ROOT.TCanvas(f'{sampleName}_canvas', f'{sampleName}_canvas', 1400, 1000)
            theCanvas.Divide(1,3)
            scorePad = theCanvas.GetPad(1)
            scorePad.SetPad(0.0, 0.6, 1.0, 1.0)
            neutrinoRatioPad = theCanvas.GetPad(2)
            neutrinoRatioPad.SetPad(0.0,0.375, 1.0, 0.6)
            dataRatioPad = theCanvas.GetPad(3)
            dataRatioPad.SetPad(0.0, 0.0, 1.0, 0.375)
            scorePad.cd()

            scorePad.SetBottomMargin(0.0)
            neutrinoRatioPad.SetBottomMargin(0.0)
            neutrinoRatioPad.SetTopMargin(0.0)
            dataRatioPad.SetBottomMargin(0.4)
            dataRatioPad.SetTopMargin(0.0)

            ###############################
            # MAIN SCORE PLOT
            ###############################
            
            scorePad.SetLogy()

            TrainZeroBias.Draw("HIST")
            TestZeroBias.Draw("HIST SAME")
            SingleNeutrino.Draw("HIST SAME")
            sample.Draw("HIST SAME")

            #TrainZeroBias.GetYaxis().SetRangeUser(-0.001, 0.08)

            TrainZeroBias.GetXaxis().SetTitle("")
            TrainZeroBias.GetXaxis().SetLabelSize(0.0)
            TrainZeroBias.GetXaxis().SetTickSize(0.0)
            TrainZeroBias.GetYaxis().SetTitle("Events (normalized to 1)")
            
            cmsLatex = ROOT.TLatex()
            cmsLatex.SetTextSize(0.05)
            cmsLatex.SetNDC(True)
            cmsLatex.SetTextAlign(32)
            cmsLatex.DrawLatex(0.9,0.92, "#font[61]{CMS} #font[52]{Preliminary}")
            
            theLegend = ROOT.TLegend(0.15, 0.8, 0.9, 0.9)
            theLegend.SetNColumns(2)
            theLegend.AddEntry(TrainZeroBias, "Data (training subset)", "l")
            theLegend.AddEntry(TestZeroBias, "Data(testing subset)", "l")
            theLegend.AddEntry(SingleNeutrino, "Single Neutrino Gun", "l")
            theLegend.AddEntry(sample, f"{sampleName}", "l")
            theLegend.SetLineWidth(0)
            theLegend.SetFillStyle(0)

            theLegend.Draw()
            
            #############################
            # RATIO TO DATA PLOT
            #############################

            dataRatioPad.cd()
            dataRatioPad.SetLogy()
            dataRatioPad.SetGridy()
            denomPlot = TestZeroBias.Clone()
        
            testDataRatio = TestZeroBias.Clone()
            testDataRatio.Divide(denomPlot)

            trainDataRatio = TrainZeroBias.Clone()
            trainDataRatio.Divide(denomPlot)
            
            sampleDataRatio = sample.Clone()
            sampleDataRatio.Divide(denomPlot)

            singleNeutrinoDataRatio = SingleNeutrino.Clone()
            singleNeutrinoDataRatio.Divide(denomPlot)

            trainDataRatio.Draw("HIST")
            testDataRatio.Draw("HIST SAME")
            singleNeutrinoDataRatio.Draw("HIST SAME")
            sampleDataRatio.Draw("HIST SAME")
            
            if "HT" in score:
                xAxisTitle = 'HT'
            else:
                xAxisTitle = "CICADA Score"
            trainDataRatio.GetXaxis().SetTitle(xAxisTitle)
            trainDataRatio.GetXaxis().SetTitleSize(0.1)
            trainDataRatio.GetXaxis().SetTickSize(0.05)
            trainDataRatio.SetLabelSize(0.1)

            trainDataRatio.GetYaxis().SetRangeUser(1.0e-2 * 0.8 ,1.0e2 * 1.5)
            trainDataRatio.GetYaxis().SetTitleSize(0.05)
            trainDataRatio.GetYaxis().SetNdivisions(5,0,0)
            trainDataRatio.GetYaxis().SetTitle("Ratio to Test Data")

            ##############################
            # RATIO TO SINGLE NEUTRINO
            ##############################
            
            neutrinoRatioPad.cd()
            neutrinoRatioPad.SetLogy()
            neutrinoRatioPad.SetGridy()
            nDenomPlot = SingleNeutrino.Clone()
            
            testNeutrinoRatio = TestZeroBias.Clone()
            testNeutrinoRatio.Divide(nDenomPlot)
            
            trainNeutrinoRatio = TrainZeroBias.Clone()
            trainNeutrinoRatio.Divide(nDenomPlot)

            sampleNeutrinoRatio = sample.Clone()
            sampleNeutrinoRatio.Divide(nDenomPlot)
            
            neutrinoNeutrinoRatio = SingleNeutrino.Clone()
            neutrinoNeutrinoRatio.Divide(nDenomPlot)

            neutrinoNeutrinoRatio.Draw("HIST")
            testNeutrinoRatio.Draw("HIST SAME")
            trainNeutrinoRatio.Draw("HIST SAME")
            sampleNeutrinoRatio.Draw("HIST SAME")

            neutrinoNeutrinoRatio.GetYaxis().SetTickSize(0.0)
            neutrinoNeutrinoRatio.SetTitle("")

            neutrinoNeutrinoRatio.GetYaxis().SetRangeUser(1.0e-2 * 0.8 ,1.0e2 * 1.5)
            neutrinoNeutrinoRatio.GetYaxis().SetTitleSize(0.07)
            neutrinoNeutrinoRatio.GetYaxis().SetNdivisions(5,0,0)
            neutrinoNeutrinoRatio.GetYaxis().SetTitle("Ratio to Neutrino Gun")

            quietROOTFunc(theCanvas.SaveAs)(
                os.path.join(outputDirectory, f'{sampleName}_{score}.png')
            )
    theFile.Close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Draw individual score plots for paper deliberations")

    args = parser.parse_args()

    main(args)

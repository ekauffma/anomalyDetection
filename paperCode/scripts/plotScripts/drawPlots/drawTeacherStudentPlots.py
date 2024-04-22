import ROOT
import argparse
from rich.console import Console
from rich.progress import track
import pathlib
import numpy as np
import re
from anomalyDetection.anomalyTriggerSkunkworks.utilities.decorators import quietROOTFunc

console = Console()

def drawColumnNormalizedDeltaScatter(theFile, histoName, yAxisName, outputPath):
    theCanvas = ROOT.TCanvas(f"{histoName}_canvas", f"{histoName}_Canvas")

def drawDeltaScatter(theFile, histoName, yAxisName, outputPath):
    theCanvas = ROOT.TCanvas(f"{histoName}_Canvas", f"{histoName}_Canvas")
    theHisto = theFile.Get(histoName)
    outputName = outputPath / f"{histoName}.png"

    theHisto.Draw("COLZ TEXT")
    theHisto.GetXaxis().SetTitle("Adjusted Teacher Score")
    theHisto.GetYaxis().SetTitle(yAxisName)

    quietROOTFunc(theCanvas.SaveAs)(str(outputName))

def drawScorePlot(theFile, histoName, xAxisName, outputPath):
    theCanvas = ROOT.TCanvas(f"{histoName}_Canvas", f"{histoName}_Canvas")
    theCanvas.SetLogy()
    theHisto = theFile.Get(histoName).Clone()
    outputName = outputPath / f"{histoName}.png"
    
    theHisto.Scale(1.0/theHisto.Integral())

    theHisto.SetLineColor(ROOT.kRed)
    theHisto.SetLineWidth(2)

    theHisto.Draw("HIST")
    theHisto.GetXaxis().SetTitle(xAxisName)
    theHisto.GetYaxis().SetTitle("Events (normalized to 1)")
    
    quietROOTFunc(theCanvas.SaveAs)(str(outputName))

def drawErrorPlot(theFile, histoName, xAxisName, outputPath):
    theCanvas = ROOT.TCanvas(f"{histoName}_Canvas", f"{histoName}_Canvas")
    theCanvas.SetLogy()
    theHisto = theFile.Get(histoName).Clone()
    outputName = outputPath/f"{histoName}.png"

    theHisto.Scale(1.0/theHisto.Integral())

    theHisto.SetLineColor(ROOT.kBlack)
    theHisto.SetLineWidth(2)

    theHisto.Draw("Hist")
    theHisto.GetXaxis().SetTitle(xAxisName)
    theHisto.GetYaxis().SetTitle("Events (normalized to 1)")
    
    quietROOTFunc(theCanvas.SaveAs)(str(outputName))

def drawAllDeltaScatters(theFile, listOfRelevantKeys, yAxisName, outputPath):
    console.log(f"Number of delta scatters: {len(listOfRelevantKeys):>6d}")
    for keyName in track(listOfRelevantKeys, description="Drawing delta scatters."):
        try:
            drawDeltaScatter(theFile, keyName, yAxisName, outputPath)
        except:
            console.log(f':warning-emoji: {keyName} failed')

def drawAllScorePlots(theFile, listOfRelevantKeys, xAxisName, outputPath):
    console.log(f"Number of score plots: {len(listOfRelevantKeys):>6d}")
    for keyName in track(listOfRelevantKeys, description="Drawing score plots"):
        try:
            drawScorePlot(theFile, keyName, xAxisName, outputPath)
        except:
            console.log(f':warning-emoji: {keyName} failed')
        
def drawAllErrorPlots(theFile, listOfRelevantKeys, xAxisName, outputPath):
    console.log(f"Number of error plots: {len(listOfRelevantKeys):>6d}")
    for keyName in track(listOfRelevantKeys, description="Draw error plots"):
        try:
            drawErrorPlot(theFile, keyName, xAxisName, outputPath)
        except:
            console.log(f':warning-emoji: {keyName} failed')

def main(args):
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPaintTextFormat("1.1g")

    basePath = pathlib.Path('/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/')
    theFile = ROOT.TFile(
        str(basePath / "TeacherStudentPlots.root")
    )

    outputPath = pathlib.Path('/nfs_scratch/aloeliger/PaperPlotFiles/FinalizedPlots/TeacherStudentPlots/')
    outputPath.mkdir(parents=True, exist_ok=True)

    listOfKeys = list(theFile.GetListOfKeys())
    listOfKeys = [x.GetName() for x in listOfKeys]

    listMatchingPattern = lambda pattern: [x for x in listOfKeys if pattern.search(x) is not None]

    console.log("Delta scatters")
    deltaScatterKeysPattern = re.compile("(?<!abs_)delta_scatter")
    deltaScatterKeys = listMatchingPattern(deltaScatterKeysPattern)
    drawAllDeltaScatters(theFile, deltaScatterKeys, "Student Score - Adjusted Teacher score", outputPath)

    console.log("Absolute Delta scatters")
    absDeltaScatterKeysPattern =re.compile("abs_delta_scatter")
    absDeltaScatterKeys = listMatchingPattern(absDeltaScatterKeysPattern)
    drawAllDeltaScatters(theFile, absDeltaScatterKeys, "|Student - Adjusted Teacher|", outputPath)

    console.log("Adjusted Teacher Scores")
    adjustedTeacherKeyPattern = re.compile("teacher_adjusted_score")
    adjustedTeacherKeys = listMatchingPattern(adjustedTeacherKeyPattern)
    drawAllScorePlots(theFile, adjustedTeacherKeys, "Adjusted Teacher Score", outputPath)

    console.log("Teacher Scores")
    teacherKeyPattern = re.compile("teacher_score")
    teacherKeys = listMatchingPattern(teacherKeyPattern)
    drawAllScorePlots(theFile, teacherKeys, "Teacher Score", outputPath)

    console.log("Student Scores")
    studentKeyPattern = re.compile("student_score")
    studentKeys = listMatchingPattern(studentKeyPattern)
    drawAllScorePlots(theFile, studentKeys, "Student score", outputPath)

    console.log("Student Errors")
    studentErrorPattern = re.compile("student_errors")
    studentErrorKeys = listMatchingPattern(studentErrorPattern)
    drawAllErrorPlots(theFile, studentErrorKeys, "Student error", outputPath)
    
    console.log("Abs Student Errors")
    absStudentErrorPattern = re.compile('student_abs_errors')
    absStudentErrorKeys = listMatchingPattern(absStudentErrorPattern)
    drawAllErrorPlots(theFile, absStudentErrorKeys, "|Student Error|", outputPath)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    args = parser.parse_args()

    main(args)

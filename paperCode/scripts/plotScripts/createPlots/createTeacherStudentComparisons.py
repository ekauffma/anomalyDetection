import ROOT
import argparse
from anomalyDetection.paperCode.samples.paperSampleBuilder import samples
from anomalyDetection.paperCode.plottingUtilities.models import *
from rich.console import Console
from rich.progress import track
import os
import pathlib

console = Console()

def createDeltaScatter(frame, sampleName, theTeacherStudentPair):
    histoName = f"{sampleName}_{theTeacherStudentPair.teacherModel.modelName}_{theTeacherStudentPair.studentModel.modelName}_delta_scatter"
    scatterModel = ROOT.RDF.TH2DModel(
        histoName,
        histoName,
        20,
        0.0,
        256.0,
        20,
        -50.0, 
        50.0,
    )

    scatterBooking = frame.Histo2D(
        scatterModel,
        theTeacherStudentPair.adjustedTeacherScoreName,
        theTeacherStudentPair.studentScoreDeltaName,
    )

    return scatterBooking
    

def createAbsDeltaScatter(frame, sampleName, theTeacherStudentPair):
    histoName = f"{sampleName}_{theTeacherStudentPair.teacherModel.modelName}_{theTeacherStudentPair.studentModel.modelName}_abs_delta_scatter"
    scatterModel = ROOT.RDF.TH2DModel(
        histoName,
        histoName,
        20,
        0.0,
        256.0,
        20,
        0.0,
        50.0,
    )

    scatterBooking = frame.Histo2D(
        scatterModel,
        theTeacherStudentPair.adjustedTeacherScoreName,
        theTeacherStudentPair.absStudentScoreDeltaName,
    )

    return scatterBooking

def createTeacherAdjustedScorePlot(frame, sampleName, theTeacherStudentCollection):
    histoName = f"{sampleName}_{theTeacherStudentCollection.teacherModel.modelName}_teacher_adjusted_score"
    scoreModel = ROOT.RDF.TH1DModel(
        histoName,
        histoName,
        50,
        0.0,
        256.0,
    )

    scoreBooking = frame.Histo1D(
        scoreModel,
        theTeacherStudentCollection.adjustedTeacherScoreName,
    )
    return scoreBooking

def createTeacherScorePlot(frame, sampleName, theTeacherStudentCollection):
    histoName = f"{sampleName}_{theTeacherStudentCollection.teacherModel.modelName}_teacher_score"
    scoreModel = ROOT.RDF.TH1DModel(
        histoName,
        histoName,
        50,
        0.0,
        100.0,
    )

    scoreBooking = frame.Histo1D(
        scoreModel,
        theTeacherStudentCollection.teacherModel.scoreName,
    )

def createStudentScorePlot(frame, sampleName, theTeacherStudentPair):
    histoName = f"{sampleName}_{theTeacherStudentPair.studentModel.modelName}_student_score"
    scoreModel = ROOT.RDF.TH1DModel(
        histoName,
        histoName,
        50,
        0.0,
        256.0
    )

    scoreBooking = frame.Histo1D(
        scoreModel,
        theTeacherStudentPair.studentModel.scoreName
    )
    return scoreBooking

def createStudentErrorHist(frame, sampleName, theTeacherStudentPair):
    histoName = f"{sampleName}_{theTeacherStudentPair.teacherModel.modelName}_{theTeacherStudentPair.studentModel.modelName}_student_errors"
    errorModel = ROOT.RDF.TH1DModel(
        histoName,
        histoName,
        50,
        -50.0,
        50.0,
    )

    errorBooking = frame.Histo1D(
        errorModel,
        theTeacherStudentPair.studentScoreDeltaName
    )

    return errorBooking

def createStudentAbsErrorHist(frame, sampleName, theTeacherStudentPair):
    histoName =f"{sampleName}_{theTeacherStudentPair.teacherModel.modelName}_{theTeacherStudentPair.studentModel.modelName}_student_abs_errors"
    errorModel = ROOT.RDF.TH1DModel(
        histoName,
        histoName,
        50,
        0.0,
        50.0,
    )

    errorBooking = frame.Histo1D(
        errorModel,
        theTeacherStudentPair.absStudentScoreDeltaName
    )

    return errorBooking

def bookPlots(dataframe, sampleName, teacherStudentModels):
    #Create teacher/ student delta scatter plots
    plots = []
    for teacherStudentGroup in teacherStudentModels:
        plots.append(
            createTeacherAdjustedScorePlot(dataframe, sampleName, teacherStudentGroup)
        )
        plots.append(
            createTeacherScorePlot(dataframe, sampleName, teacherStudentGroup)
        )
        for theTeacherStudentPair in teacherStudentGroup.teacherStudentPairs:
            plots.append(
                createDeltaScatter(dataframe, sampleName, theTeacherStudentPair)
            )
            plots.append(
                createAbsDeltaScatter(dataframe, sampleName, theTeacherStudentPair)
            )
            plots.append(
                createStudentScorePlot(dataframe, sampleName, theTeacherStudentPair)
            )
            plots.append(
                createStudentErrorHist(dataframe, sampleName, theTeacherStudentPair)
            )
            plots.append(
                createStudentAbsErrorHist(dataframe, sampleName, theTeacherStudentPair)
            )
    return plots
            
def main(args):
    sampleNames = list(samples.keys())
    #debug
    #sampleNames = sampleNames[:1]
    dataFrames = dict(
        [
            (sampleName, samples[sampleName].getNewDataframe()) for sampleName in sampleNames
        ]
    )

    teacherStudentModels = [
        CICADA_vXp2p0_Group,
        CICADA_vXp2p0N_Group,
        CICADA_vXp2p1_Group,
        CICADA_vXp2p1N_Group,
    ]
    
    plots = []
    for sampleName in track(dataFrames, description="Deriving values and booking plots..."):
        frame = dataFrames[sampleName]
        for teacherStudentModel in teacherStudentModels:
            frame = teacherStudentModel.applyFrameDefinitions(frame)

        plots += bookPlots(frame, sampleName, teacherStudentModels)

    plotOutputLocation = pathlib.Path('/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles')
    plotOutputLocation.mkdir(parents=True, exist_ok=True)
    outputFileName = plotOutputLocation/'TeacherStudentPlots.root'
    console.log(f"Saving to {outputFileName}")
    
    theOutputFile = ROOT.TFile(str(outputFileName), 'RECREATE')
    for plot in track(plots, description="Writing plots"):
        plot.Write()
    theOutputFile.Write()
    theOutputFile.Close()
    console.log(f'[bold green]\[Done][/bold green] Writing files')
    
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create teacher student comparisons")

    args=parser.parse_args()

    main(args)

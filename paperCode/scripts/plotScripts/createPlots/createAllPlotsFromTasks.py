# !/usr/bin/env python3

import argparse
from rich.console import Console
from rich.table import Table
import multiprocessing
from time import perf_counter, sleep

from anomalyDetection.paperCode.plottingCore.plotTask import createPlotTask

from anomalyDetection.paperCode.plottingTasks.createScorePlotTask import createScorePlotTask
from anomalyDetection.paperCode.plottingTasks.createTeacherStudentPlotTask import createTeacherStudentPlotTask
from anomalyDetection.paperCode.plottingTasks.createHTCorrelationPlotTask import createHTCorrelationPlotTask
from anomalyDetection.paperCode.plottingTasks.createSignalAdditionsPlotTask import createSignalAdditionsPlotTask
from anomalyDetection.paperCode.plottingTasks.createCICADATurnOnPlotTask import createCICADATurnOnPlotTask
from anomalyDetection.paperCode.plottingTasks.createCICADAPurityContentPlotTask import createCICADAPurityContentPlotTask
from anomalyDetection.paperCode.plottingTasks.createObjectCorrelationPlotsTask import createObjectCorrelationPlotsTask

from anomalyDetection.paperCode.samples.paperSampleBuilder import reducedSamples as samples

#debug
# samples = dict(
#     [
#         (
#             "GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8",
#             samples["GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8"],
#         ),
#         (
#             "ZeroBias",
#             samples["ZeroBias"],
#         )
#     ]
# )

console = Console()
resultQueue = multiprocessing.Queue()

# a quick binding runner
def runTask(theTask: createPlotTask):
    start_time = perf_counter()
    localConsole = Console()
    #localConsole.log(f"Task: {theTask.taskName} started")
    try:
        theTask.executeTask()
    except Exception as err:
        end_time=perf_counter()
        localConsole.log(f'Task: {theTask.taskName} failed')
        localConsole.print_exception(max_frames=10, show_locals=True)
        #create failure result
        resultQueue.put(
            (
                theTask.taskName,
                err,
                end_time-start_time,
            )
            
        )
    else:
        end_time=perf_counter()
        resultQueue.put(
            (
                theTask.taskName,
                None,
                end_time-start_time,
            )
        )
    #localConsole.log(f"Task: {theTask.taskName} finished")

def main(args):
    scoreTask = createScorePlotTask(
        taskName="Create Score Plots",
        outputFileName="scorePlots.root",
        dictOfSamples=samples,
        nBins=40,
    )
    rocScoreTask = createScorePlotTask(
        taskName = "Create ROC Score Plots",
        outputFileName="scorePlotsForROCs.root",
        dictOfSamples=samples,
        nBins=200,
    )

    HTCorrelationTask = createHTCorrelationPlotTask(
        taskName = "Create HT Correlation Plots",
        outputFileName = "CICADA_HT_Correlation.root",
        dictOfSamples=samples,
    )
    
    teacherStudentTask = createTeacherStudentPlotTask(
        taskName="Create Teacher-Student Plots",
        outputFileName="TeacherStudentPlots.root",
        dictOfSamples=samples,
    )
    signalAdditionsTask = createSignalAdditionsPlotTask(
        taskName="Create signal additions plots",
        outputFileName="signalAdditionsPlots.root",
        dictOfSamples = samples,
        nBins=40,
    )
    CICADATurnOnTask = createCICADATurnOnPlotTask(
        taskName = "Create CICADA Turn On Curves",
        outputFileName="CICADATurnOnCurves.root",
        dictOfSamples = samples,
        nBins = 30,
    )
    CICADAPurityContentPlotTask = createCICADAPurityContentPlotTask(
        taskName = 'Create Purity Content Plots',
        outputFileName = 'CICADAPurityContent.root',
        dictOfSamples = samples,
    )
    objectCorrelationPlotsTask = createObjectCorrelationPlotsTask(
        taskName = 'Create Object Correlation Plots',
        outputFileName = 'CICADAObjectPlots.root',
        dictOfSamples = samples,
    )

    allTasks = [
        scoreTask,
        rocScoreTask,
        HTCorrelationTask,
        teacherStudentTask,
        signalAdditionsTask,
        CICADATurnOnTask,
        CICADAPurityContentPlotTask,
        objectCorrelationPlotsTask,
    ]

    start_time = perf_counter()
    with console.status("Creating plots. This may take some time"):
        p = multiprocessing.Pool(10)
        p.map(runTask, allTasks)
    end_time = perf_counter()
    console.log(f"Finished all plots in {end_time-start_time: 8.4g} seconds")

    sleep(5)

    statusTable = Table(title="Plot status")
    statusTable.add_column("Task Name")
    statusTable.add_column("Status")
    statusTable.add_column("Error")
    statusTable.add_column("Elapsed Time (s)")
    
    while not resultQueue.empty():
        result = resultQueue.get()
        taskName, err, taskTime = result[0], result[1], result[2]
        if err == None:
            statusString = '[bold green]Succeeded[/bold green]'
            errReport = "None"
        else:
            statusString = '[bold red]Failed[/bold red]'
            errReport = str(type(err))            
        statusTable.add_row(taskName, statusString, errReport, f'{taskTime:8.4g}')
    console.print(statusTable)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Rerun all analysis plots')

    args =parser.parse_args()

    main(args)

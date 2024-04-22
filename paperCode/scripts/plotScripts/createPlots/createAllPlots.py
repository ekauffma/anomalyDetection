#!/usr/bin/env python3

import argparse
from rich.console import Console
from rich.table import Table
import subprocess
import multiprocessing
from time import perf_counter

console = Console()

resultQueue = multiprocessing.Queue()

class plotTask():
    def __init__(self, name, command):
        self.name = name
        self.command = command
        self.status = None
        self.errorMessage = None
        
    def makePlot(self):
        plotProcess = subprocess.run(
            [self.command],
            capture_output=True,
            text=True,
            shell=True,
        )

        self.status = plotProcess.returncode
        if plotProcess.returncode != 0:
            self.errorMessage = plotProcess.stdout +'\n\n' + plotProcess.stderr
        resultQueue.put(
            [
                self.name,
                self.command,
                self.status,
                self.errorMessage
            ]
        )

def main(args):
    
    quickCheckScores = plotTask(
        name='Quick scores',
        command='python3 paperCode/scripts/plotScripts/createPlots/createScorePlots.py'
    )
    rocScores = plotTask(
        name='Scores for ROCs',
        command = 'python3 paperCode/scripts/plotScripts/createPlots/createScorePlots.py --ForROCs',
    )
    HTCorrelations = plotTask(
        name='HT Correlations',
        command='python3 paperCode/scripts/plotScripts/createPlots/createCICADAandHTCorrelation.py',
    )
    teacherStudentPlots = plotTask(
        name="Teacher Student Comparisons",
        command = 'python3 paperCode/scripts/plotScripts/createPlots/createTeacherStudentComparisons.py'
    )

    allTasks = [
        quickCheckScores,
        rocScores,
        HTCorrelations,
        teacherStudentPlots,
    ]

    start_time = perf_counter()
    with console.status("Running plots"):
        processes = []
        console.log("Defining tasks...")
        for task in allTasks:
            processes.append(
                multiprocessing.Process(target = task.makePlot)
            )
        console.log("Starting tasks...")
        for process in processes:
            process.start()
        console.log("Waiting for tasks to complete...")
        for process in processes:
            process.join()
    end_time = perf_counter()
    console.log(f"Finished all plots in {end_time-start_time: 8.4g} seconds")

    statusTable = Table(title="Plot status")
    statusTable.add_column("Status",no_wrap=True)
    statusTable.add_column("Name", no_wrap=True)
    statusTable.add_column("Command")
    statusTable.add_column("Error Code")

    #for task in allTasks:
    while not resultQueue.empty():
        result = resultQueue.get()
        taskName, command, status, errorMsg = result[0], result[1], result[2], result[3]
        if status != 0:
            statusString = '[bold red]Failed[/bold red]'
            console.print(f"Task: \"{task.name}\" failed")
            console.print("Command:")
            console.print(command)
            console.print("Status:")
            console.print(status)
            console.print("Error Message:")
            console.print(f"{errorMsg}")
        else:
            statusString = '[bold green]Succeeded[/bold green]'
        statusTable.add_row(statusString, taskName, command, f"{status}")
    console.print(statusTable)

if __name__ =='__main__':
    parser = argparse.ArgumentParser(description="rerun all analysis plots")
    
    args = parser.parse_args()

    main(args)

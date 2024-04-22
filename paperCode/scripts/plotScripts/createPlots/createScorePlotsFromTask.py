# !/usr/bin/env python3

from anomalyDetection.paperCode.samples.paperSampleBuilder import reducedSamples as samples

from anomalyDetection.paperCode.plottingTasks.createScorePlotTask import createScorePlotTask

#debug
samples = dict(
    [
        (
            "GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8",
            samples["GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8"],
        ),
        (
            "ZeroBias",
            samples["ZeroBias"],
        )
    ]
)

def main():
    theTask = createScorePlotTask(
        taskName = 'Create Score Plots',
        outputFileName = 'scorePlots.root',
        dictOfSamples = samples,
        nBins=40,
    )
    
    theTask.executeTask()

if __name__ == '__main__':
    main()

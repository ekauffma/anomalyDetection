from anomalyDetection.paperCode.plottingTasks.createSignalAdditionsPlotTask import createSignalAdditionsPlotTask
from anomalyDetection.paperCode.samples.paperSampleBuilder import reducedSamples as samples

#debug
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
    theTask = createSignalAdditionsPlotTask(
        taskName = 'Create Signal Additions Plot',
        outputFileName = 'signalAdditionsPlots.root',
        dictOfSamples = samples,
        nBins=40,
    )
    
    theTask.executeTask()

if __name__ == '__main__':
    main()

import h5py
import math
from sklearn.model_selection import train_test_split
import numpy as np
from tensorflow import keras
import tensorflow as tf
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from scipy.stats import rv_continuous
from rich.console import Console

console = Console()

def makeNormedInstances(theDataset):
    reshapedData = theDataset.reshape((theDataset.shape[0], -1))
    mean_values = np.mean(reshapedData, axis=1, keepdims=True)
    std_values = np.std(reshapedData, axis=1, keepdims=True)

    mean_values = mean_values.reshape((theDataset.shape[0],1,1))
    std_values = std_values.reshape((theDataset.shape[0],1,1))

    normalizedData = (theDataset - mean_values) / std_values
    return normalizedData


def makeDifferences(distribution, outputName):
    inputs = distribution.reshape((distribution.shape[0], 18*14))
    outputs = makeNormedInstances(distribution)
    predictions = teacherModel.predict(inputs)
    
    predictions = predictions.reshape((-1, 18, 14))
    
    squaredDifferences = (predictions-outputs)**2
    meanSquaredError = np.mean(squaredDifferences, axis=(1,2))

    # print(meanSquaredError)
    # print(meanSquaredError.shape)
    nBins=30
    amounts, binEdges, _ = plt.hist(
        meanSquaredError,
        bins=nBins,
        range=(0.0,1.5)
    )
    plt.xlabel("Mean squared error")
    plt.ylabel("Instances")
    plt.savefig(f'{outputDir}/teacher_loss_{outputName}.png',bbox_inches="tight")
    plt.close()

teacherModel = keras.models.load_model("models/teacher")
outputDir = Path("plots")

console.log("test")
with h5py.File("/hdfs/store/user/aloelige/CICADA_Training/22Jan2024/ZeroBias_EvenLumi.h5") as theFile:
    theDataset = np.array(theFile["CaloRegions"])
    
all_inputData = theDataset.reshape(theDataset.shape[0], 18*14)
all_outputData = makeNormedInstances(theDataset)

trainval_inputData, test_inputData, trainval_outputData,  test_outputData = train_test_split(all_inputData, all_outputData, test_size=0.4, random_state=42)
inputData, valInput, outputData, valOutput = train_test_split(trainval_inputData, trainval_outputData, test_size=0.1/(0.6), random_state=42)

makeDifferences(test_inputData.reshape(-1, 18,14), "test")

console.log("uniform")
uniformDistribution = np.random.uniform(
    0.0,
    1024.0,
    size = (100000, 18, 14)
)

makeDifferences(uniformDistribution, "uniform")

console.log("normal, mu=0, sigma=1")
normalDistribution = np.random.uniform(
    0.0,
    1.0,
    size = (100000, 18, 14)
)
makeDifferences(normalDistribution, "normal_mu_0_sigma_1")

console.log("gamma, shape=1.0")
gammaDistribution = np.random.gamma(
    1.0,
    size = (100000, 18, 14)
)
makeDifferences(gammaDistribution, "gamma_shape_1p0")

console.log("gamma, shape=2.0")
gammaDistribution = np.random.gamma(
    2.0,
    size = (100000, 18, 14)
)
makeDifferences(gammaDistribution, "gamma_shape_2p0")

console.log("gamma, shape=0.1")
gammaDistribution = np.random.gamma(
    0.1,
    size = (100000, 18, 14)
)
makeDifferences(gammaDistribution, "gamma_shape_0p1")

console.log("gamma, shape=0.001")
gammaDistribution = np.random.gamma(
    0.001,
    size = (100000, 18, 14)
)
makeDifferences(gammaDistribution, "gamma_shape_0p001")

gammaPoints = [
    0.0001,
    0.0003,
    0.0005,
    0.0007,
    0.0009,
    0.001,
    0.005,
    0.01,
    0.05,
    0.1,
    0.5,
    1.0,
    5.0,
]

for point in gammaPoints:
    console.log(point)
    gammaDistribution = np.random.gamma(
        point,
        size = (100000, 18, 14)
    )
    name = "gamma_shape_"+str(point).replace(".","p")
    makeDifferences(gammaDistribution, name)


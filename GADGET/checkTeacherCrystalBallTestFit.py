import h5py
import numpy as np
import scipy
from tensorflow import keras
import tensorflow as tf
from rich.console import Console
from sklearn.model_selection import train_test_split
from qkeras import QActivation, QConv2D, QDense, quantized_bits
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import math
from scipy.optimize import curve_fit

console = Console()

def makeNormedInstances(theDataset):
    reshapedData = theDataset.reshape((theDataset.shape[0], -1))
    mean_values = np.mean(reshapedData, axis=1, keepdims=True)
    std_values = np.std(reshapedData, axis=1, keepdims=True)

    mean_values = mean_values.reshape((theDataset.shape[0],1,1))
    std_values = std_values.reshape((theDataset.shape[0],1,1))

    normalizedData = (theDataset - mean_values) / std_values
    return normalizedData

def gauss(x, *p):
    A, mu, sigma = p
    return A * np.exp((-1/2)*((x-mu)/sigma)**2)

def crystal_ball(x, *p):
    alpha, x_bar, sigma, N = p
    n = 3.0
    A = ((n/np.abs(alpha))**n) * np.exp((-(np.abs(alpha)**2))/2)
    B = n/np.abs(alpha) - np.abs(alpha)

    condition = (x-x_bar)/sigma > -alpha
    gauss_output = N*np.exp((-(x-x_bar)**2)/(2*(sigma**2)))
    power_law = N*A*np.power((B-((x-x_bar)/sigma)), -n)

    return np.where(condition, gauss_output, power_law)

def main():
    teacherModel = keras.models.load_model("models/teacher")
    outputDir = Path("plots")

    console.log("test")
    with h5py.File("/hdfs/store/user/aloelige/CICADA_Training/22Jan2024/ZeroBias_EvenLumi.h5") as theFile:
        theDataset = np.array(theFile["CaloRegions"])
    
    all_inputData = theDataset.reshape(theDataset.shape[0], 18*14)
    all_outputData = makeNormedInstances(theDataset)
        
    trainval_inputData, test_inputData, trainval_outputData,  test_outputData = train_test_split(all_inputData, all_outputData, test_size=0.4, random_state=42)
    inputData, valInput, outputData, valOutput = train_test_split(trainval_inputData, trainval_outputData, test_size=0.1/(0.6), random_state=42)

    inputs = test_inputData.reshape((-1, 18*14))
    outputs = makeNormedInstances(test_outputData)
    predictions = teacherModel.predict(inputs, verbose=0)

    predictions = predictions.reshape((-1, 18, 14))
    
    errors = np.mean((predictions-outputs)**2, axis=(1,2))
    
    nBins=30
    amounts, binEdges, _ = plt.hist(
        errors,
        bins=nBins,
        label="Teacher Loss",
        range=(0.0,1.0)
    )
    plt.xlabel("Mean Squared Error")
    plt.ylabel("Instances")
    
    binCenters = (binEdges[:-1]+binEdges[1:])/2
    amplitudeGuess = np.max(amounts)
    centerGuess = binCenters[np.argmax(amounts)]
    sigmaGuess = (binCenters[-1]-binCenters[0])/2
    
    console.log("Gauss fit")
    gaussParameters = [amplitudeGuess, centerGuess, sigmaGuess]
    fitCoeff, var_matrix = curve_fit(gauss, binCenters, amounts, p0=gaussParameters)
    fit_x = np.linspace(min(errors), max(errors), nBins)
    plt.plot(fit_x, gauss(fit_x, *fitCoeff), 'r-', label='Gauss fit')
    
    console.log("Crystal ball fit")
    crystalBallParameters=[1.0, centerGuess, sigmaGuess, 1.0]
    console.log(crystalBallParameters)
    crystalBallCoeffs, crystalBallmatrix = curve_fit(crystal_ball, binCenters, amounts, p0=crystalBallParameters, maxfev=10000)
    console.print(crystalBallCoeffs)
    fit_x = np.linspace(min(errors), max(errors), nBins)
    plt.plot(fit_x, crystal_ball(fit_x, *crystalBallCoeffs), 'g-', label='Crystal Ball Fit')

    plt.legend(loc="upper right")
    plt.savefig(f'plots/teacher_fits.png')
    plt.close()

if __name__=='__main__':
    main()

import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

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

#TODO: Duplicate. Offload
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

def makeStudentTargetWeightsGivenGenerator(inputs, trueValues, model, weightGenerator):
    modelPredictions = model.predict(inputs, verbose=0).reshape((-1, 18, 14))
    mses = tf.math.reduce_mean((trueValues - modelPredictions)**2, axis=[1,2])
    
    unNormalizedWeights = weightGenerator(mses)
    normalizedWeights = unNormalizedWeights * (len(unNormalizedWeights)/np.sum(unNormalizedWeights))
    return normalizedWeights

def makeStudentTargetWeights(inputs, trueValues, model):
    modelPredictions = model.predict(inputs, verbose=0).reshape((-1, 18, 14))
    mses = tf.math.reduce_mean((trueValues-modelPredictions)**2, axis=[1,2])
    
    nBins = 30
    hist, x_edges = np.histogram(mses, bins=nBins)

    binCenters = (x_edges[:-1]+x_edges[1:])/2
    amplitudeGuess = np.max(hist)
    centerGuess = binCenters[np.argmax(hist)]
    sigmaGuess = (binCenters[-1]-binCenters[0])/2

    gaussParameters = [amplitudeGuess, centerGuess, sigmaGuess]
    fitCoeff, fitMatrix = curve_fit(gauss, binCenters, hist, p0=gaussParameters)
    fix_x = np.linspace(min(mses), max(mses), nBins)

    unNormalizedWeightGeneration = lambda x: 1.0/gauss(x, fitCoeff[0], fitCoeff[1], fitCoeff[2])
    unNormalizedWeights = unNormalizedWeightGeneration(mses)
    normalizedWeights = unNormalizedWeights * (len(unNormalizedWeights)/np.sum(unNormalizedWeights))
    return normalizedWeights, unNormalizedWeightGeneration

def makeStudentTargetWeightsFromStudentTargetsGivenGenerator(studentTargets, generator):
    unNormalizedWeights = generator(studentTargets)
    normalizedWeights = unNormalizedWeights*(len(unNormalizedWeights)/np.sum(unNormalizedWeights))
    return normalizedWeights

def makeStudentTargetWeightsFromStudentTargets(studentTargets):
    nBins = 30,
    hist, x_edges = np.histogram(studentTargets)

    binCenters = (x_edges[:-1]+x_edges[1:])/2
    amplitudeGuess = np.max(hist)
    centerGuess = (binCenters[np.argmax(hist)])
    sigmaGuess = (binCenters[-1]-binCenters[0])/2
    
    gaussParameters = [amplitudeGuess, centerGuess, sigmaGuess]
    fitCoeff, fitMatrix = curve_fit(gauss, binCenters, hist, p0=gaussParameters)
    
    unNormalizedWeightGeneration = lambda x: 1.0/gauss(x, fitCoeff[0], fitCoeff[1], fitCoeff[2])
    normalizedWeights = makeStudentTargetWeightsFromStudentTargetsGivenGenerator(studentTargets, unNormalizedWeightGeneration)

    return normalizedWeights, unNormalizedWeightGeneration

def linearShiftTargets(targets, m, b):
    return m*targets + b

def makeTargetsGivenShift(inputs, trueValues, model, m, b):
    modelPredictions = model.predict(inputs, verbose=0).reshape((-1, 18, 14))
    mses = np.mean((trueValues-modelPredictions)**2, axis=(1,2))
    shiftedScores = linearShiftTargets(mses, m, b)
    return shiftedScores    

def makeStudentTargets(inputs, trueValues, model):
    currentTargets = model.predict(
        inputs,
        verbose=0,
    )
    currentTargets = tf.reshape(currentTargets, [-1,18,14])
    currentTargets = tf.math.reduce_mean((currentTargets-trueValues)**2, axis=[1,2])

    oldMax = tf.math.reduce_max(currentTargets)
    oldMin = tf.math.reduce_min(currentTargets)

    newMax = (2**8)-(2**-8)
    newMin = 2**-8

    m = (newMax-newMin)/(oldMax-oldMin)
    b = (newMin*oldMax - newMax*oldMin)/(oldMax-oldMin)

    currentTargets = linearShiftTargets(currentTargets, m, b)

    return currentTargets, m, b

def main():
    #TODO: Duplicate. Offload
    with h5py.File("/hdfs/store/user/aloelige/CICADA_Training/22Jan2024/ZeroBias_EvenLumi.h5") as theFile:
        theDataset = np.array(theFile["CaloRegions"])
    
    # Random inputs
    # theDataset = np.random.gamma(
    #     0.0008,
    #     size = (len(theDataset), 18, 14)
    # )
    #theDataset = np.append(theDataset, gammaInputs, axis=0)
    # theDataset = np.append(
    #     theDataset,
    #     np.random.gamma(
    #         0.1,
    #         size=(len(theDataset)//2, 18, 14),
    #     ),
    #     axis=0
    # )
    # theDataset = np.append(
    #     theDataset,
    #     np.random.gamma(
    #         0.001,
    #         size=(len(theDataset)//2, 18, 14),
    #     ),
    #     axis=0
    # )

    #theDataset = theDataset[:10000]

    all_inputData = theDataset.reshape(theDataset.shape[0], 18*14)
    all_outputData = makeNormedInstances(theDataset)

    trainval_inputData, test_inputData, trainval_outputData,  test_outputData = train_test_split(all_inputData, all_outputData, test_size=0.4, random_state=42)
    inputData, valInput, outputData, valOutput = train_test_split(trainval_inputData, trainval_outputData, test_size=0.1/(0.6), random_state=42)

    print(inputData.shape)
    print(outputData.shape)

    cicada_v1 = keras.models.Sequential([
        keras.layers.Input(shape=inputData.shape[1:], name='cicada_v1_input'),
        keras.layers.LayerNormalization(axis=1, name='cicada_v1_layernorm'),
        QDense(
            16,
            kernel_quantizer=quantized_bits(8, 1, 1, alpha=1.0),
            bias_quantizer=quantized_bits(8, 3, 1, alpha=1.0),
            name='cicada_v1_dense_1'
        ),
        QActivation("quantized_relu(10, 6)", name='cicada_v1_activation_1'),
        keras.layers.Dropout(1/8, name='cicada_v1_drop_1'),
        QDense(
            1,
            kernel_quantizer=quantized_bits(12, 3, 1, alpha=1.0),
            use_bias = False,
            name='cicada_v1_dense_2'
        ),
        QActivation("quantized_relu(16,8)", name='cicada_v1_activation_2')
    ])
    cicada_v1.compile(
        loss='mae',
        #metrics = [keras.metrics.RootMeanSquaredError()],
        weighted_metrics = [keras.metrics.MeanAbsolutePercentageError()],
        optimizer=keras.optimizers.Adam(learning_rate=0.001)
    )
    cicada_v1_BestModel = keras.callbacks.ModelCheckpoint("models/cicada_v1", save_best_only=True)
    cicada_v1_Log = keras.callbacks.CSVLogger(f"models/cicada_v1/training.log", append=True)
    cicada_v1_nan = keras.callbacks.TerminateOnNaN()

    cicada_v1.summary()

    numEpochs = 200
    console.log("Making student targets...")
    best_teacher = keras.models.load_model("models/teacher")
    
    studentTargets, linearShift_m, linearShift_b = makeStudentTargets(inputData, outputData, best_teacher)
    console.log(f"Linear shift slope: {linearShift_m}")
    console.log(f"Linear shift bias: {linearShift_b}")
    valStudentTargets = makeTargetsGivenShift(valInput, valOutput, best_teacher, linearShift_m, linearShift_b)

    console.log("Making student Weights...")
    # trainWeights, weightGenerator = makeStudentTargetWeights(inputData, outputData, best_teacher)
    # valWeights = makeStudentTargetWeightsGivenGenerator(valInput, valOutput, best_teacher, weightGenerator)
    trainWeights, weightGenerator = makeStudentTargetWeightsFromStudentTargets(studentTargets)
    valWeights = makeStudentTargetWeightsFromStudentTargetsGivenGenerator(valStudentTargets, weightGenerator)
    
    console.log("First 100 student targets")
    console.log(list(zip(enumerate(studentTargets[:100]))))
    console.log("First 100 student weights")
    console.log(list(zip(enumerate(trainWeights[:100]))))
    console.log("First 20 Particularly high scores:")
    mask = studentTargets > 175.0
    highScores = np.array(studentTargets)[mask]
    console.log(list(zip(enumerate(highScores[:20]))))
    console.log("Corresponding weights:")
    console.log(list(zip(enumerate(trainWeights[mask][:20]))))

    cicada_v1.fit(
        x=inputData,
        y=studentTargets,
        epochs = numEpochs,
        sample_weight = trainWeights,
        validation_data=(valInput, valStudentTargets, valWeights),
        callbacks=[cicada_v1_BestModel, cicada_v1_Log, cicada_v1_nan],
    )
    


if __name__ == '__main__':
    main()


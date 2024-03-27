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

#TODO: Duplicate, remove
def linearShiftTargets(targets, m, b):
    return m*targets + b

def drawStudentVsTeacher(studentModel, teacherModel, testInputs, testOutputs, outputDir, linearShift_m, linearShift_b):
    teacherModelOutputs = teacherModel.predict(
        testInputs,
        verbose=0,
    )
    teacherModelOutputs = tf.reshape(teacherModelOutputs, [-1, 18, 14])
    teacherErrors = tf.math.reduce_mean((teacherModelOutputs-testOutputs)**2, axis=[1,2])
    studentTargets = linearShiftTargets(teacherErrors, linearShift_m, linearShift_b)

    studentPredictions = studentModel.predict(testInputs, verbose=0)
    studentPredictions = studentPredictions.reshape((studentPredictions.shape[0]))

    console.print("Here are some high score student targets")
    highScoreMask = studentTargets > 175.0
    highScores = studentTargets[highScoreMask]
    console.print(highScores[:20])
    console.print("And here are the actual predictions")
    console.print(studentPredictions[highScoreMask][:20])

    console.print("Here are some random targets")
    console.print(studentTargets[:20])
    console.print("And here are their predictions")
    console.print(studentPredictions[:20])

    errors = np.absolute(np.subtract(studentPredictions, studentTargets.numpy()))

    #plt.scatter(
    #    studentTargets,
    #    errors,
    #)
    hist, x_edges, y_edges = np.histogram2d(
        studentTargets,
        errors,
        bins=30,
    )

    column_sums = np.sum(hist, axis=0)

    normalized_hist = hist / column_sums[np.newaxis, :]

    # Plot the normalized histogram
    plt.imshow(normalized_hist, interpolation='nearest', origin='lower',
               extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]])
    plt.colorbar(label='Normalized Counts')
    plt.xlabel("Adjusted Teacher scores")
    plt.ylabel("Student Errors")
    plt.show()

    plt.savefig(
        f"{outputDir}/GADGETv1_Error.png",
        bbox_inches="tight"
    )
    plt.close()

def makeNormedInstances(theDataset):
    reshapedData = theDataset.reshape((theDataset.shape[0], -1))
    mean_values = np.mean(reshapedData, axis=1, keepdims=True)
    std_values = np.std(reshapedData, axis=1, keepdims=True)

    mean_values = mean_values.reshape((theDataset.shape[0],1,1))
    std_values = std_values.reshape((theDataset.shape[0],1,1))

    normalizedData = (theDataset - mean_values) / std_values
    return normalizedData

def main():
    with h5py.File("/hdfs/store/user/aloelige/CICADA_Training/22Jan2024/ZeroBias_EvenLumi.h5") as theFile:
        theDataset = np.array(theFile["CaloRegions"])

    all_inputData = theDataset.reshape(theDataset.shape[0], 18*14)
    all_outputData = makeNormedInstances(theDataset)

    trainval_inputData, test_inputData, trainval_outputData,  test_outputData = train_test_split(all_inputData, all_outputData, test_size=0.4, random_state=42)
    inputData, valInput, outputData, valOutput = train_test_split(trainval_inputData, trainval_outputData, test_size=0.1/(0.6), random_state=42)

    studentModel = keras.models.load_model("models/cicada_v1")
    teacherModel = keras.models.load_model("models/teacher")
    linearShift_m = 313.59710693359375
    linearShift_b = -8.103662490844727
    outputDir = Path("plots")

    drawStudentVsTeacher(studentModel, teacherModel, test_inputData, test_outputData, outputDir, linearShift_m, linearShift_b)

if __name__ == '__main__':
    main()

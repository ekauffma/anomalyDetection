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


def main():
    with h5py.File("/hdfs/store/user/aloelige/CICADA_Training/22Jan2024/ZeroBias_EvenLumi.h5") as theFile:
        theDataset = np.array(theFile["CaloRegions"])

    all_inputData = theDataset.reshape(theDataset.shape[0], 18*14)
    all_outputData = makeNormedInstances(theDataset)

    trainval_inputData, test_inputData, trainval_outputData,  test_outputData = train_test_split(all_inputData, all_outputData, test_size=0.4, random_state=42)
    inputData, valInput, outputData, valOutput = train_test_split(trainval_inputData, trainval_outputData, test_size=0.1/(0.6), random_state=42)

    print(inputData.shape)
    print(outputData.shape)

    ae_model = keras.models.Sequential([
        keras.layers.Input(shape=inputData.shape[1:], name="teacher_input"),
        keras.layers.Reshape((18,14,1), name='teacher_reshape'),
        keras.layers.LayerNormalization(axis=[1,2,3], name='teacher_layer_norm'),
        keras.layers.Conv2D(
            filters=20,
            kernel_size=3,
            strides=1,
            padding="same",
            activation='relu',
            name='teacher_conv2d_1'
        ),
        keras.layers.AveragePooling2D(
            pool_size=2,
            name='teacher_averagepool_1'
        ),
        keras.layers.Conv2D(
            filters=30,
            kernel_size=3,
            strides=1,
            padding='same',
            activation='relu',
            name='teacher_conv2d_2'
        ),
        keras.layers.Flatten(name='teacher_flatten_1'),
        keras.layers.Dense(80, activation='relu', name='teacher_dense_1'),
        keras.layers.Dense(9*7*30, name='teacher_dense_2'),
        keras.layers.Reshape((9,7,30), name='teacher_reshape_2'),
        keras.layers.Activation('relu', name='teacher_activation_1'),
        keras.layers.Conv2D(
            filters=30,
            kernel_size=3,
            strides=1,
            padding='same',
            activation='relu',
            name='techer_conv2d_3'
        ),
        keras.layers.UpSampling2D((2,2), name='teacher_upsample_1'),
        keras.layers.Conv2D(
            filters=20,
            kernel_size=3,
            strides=1,
            padding='same',
            activation='relu',
            name='teacher_conv2d_4'
        ),
        keras.layers.Conv2D(
            filters=1,
            kernel_size=3,
            strides=1,
            padding='same',
            #activation='relu',
            name='teacher_conv2d_5'
        )        
    ])
    
    ae_model.compile(
        loss='mse',
        metrics = [keras.metrics.MeanAbsoluteError(), keras.metrics.MeanAbsolutePercentageError()],
        optimizer=keras.optimizers.Adam(learning_rate=0.001)
    )
    teacherBestModel = keras.callbacks.ModelCheckpoint("models/teacher", save_best_only=True)
    teacherLog = keras.callbacks.CSVLogger(f"models/teacher/training.log", append=False)

    ae_model.summary()
    
    console.print("Example input")
    console.print(inputData[:1])
    console.print("Corresponding output")
    console.print(outputData[:1])

    numEpochs = 20
    
    ae_model.fit(
        x=inputData,
        y=outputData,
        validation_data=(valInput, valOutput),
        epochs=numEpochs,
        callbacks=[teacherBestModel, teacherLog]
    )

if __name__ == '__main__':
    main()

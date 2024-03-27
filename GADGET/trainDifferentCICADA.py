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

def drawLossHistory(modelName, outputDir):
    log = pd.read_csv(f"models/{modelName}/training.log")
    plt.plot(np.arange(1, len(log["loss"])+1), log["loss"], label="Training")
    plt.plot(np.arange(1, len(log["val_loss"])+1), log["val_loss"], label="Validation")
    plt.legend(loc="upper right")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.savefig(
        f"{outputDir}/{modelName}_Loss.png",
        bbox_inches="tight",
    )
    plt.close()

def drawTeacherErrors(testInputs, testOutputs, outputDir):
    teacherModel = keras.models.load_model("models/teacher")
    teacherPredictions = teacherModel.predict(
        testInputs,
        verbose=0,
    )
    teacherPredictions = teacherPredictions.reshape(-1, 18, 14)
    mse = np.mean(
        np.subtract(teacherPredictions, testOutputs)**2,
        axis=(1,2),
    )

    nBins = 30
    amounts, binEdges, _ = plt.hist(
        mse,
        bins=nBins,
        alpha=0.6,
        label='Teacher errors'
    )
    plt.xlabel("Teacher MSE")
    plt.ylabel("Instances")

    #try fitting a gauss to this to check how good it is
    binCenters = (binEdges[:-1]+binEdges[1:])/2
    amplitudeGuess = np.max(amounts)
    centerGuess = binCenters[np.argmax(amounts)]
    sigmaGuess = (binCenters[-1]-binCenters[0])/2

    gaussParameters = [amplitudeGuess, centerGuess, sigmaGuess]
    fitCoeff, var_matrix = curve_fit(gauss, binCenters, amounts, p0=gaussParameters)
    fit_x = np.linspace(min(mse), max(mse), nBins)
    plt.plot(fit_x, gauss(fit_x, *fitCoeff), 'r-', label='Gauss fit')

    #try fitting a crystal ball
    crystalBallParameters = [2.0, centerGuess, sigmaGuess]
    crystalBallCoeffs, crystalBallMatrix = curve_fit(crystal_ball, binCenters, amounts, p0=crystalBallParameters)
    plt.plot(fit_x, crystal_ball(fit_x, *crystalBallCoeffs), 'g-', label='Crystal Ball Fit')

    plt.savefig(f'{outputDir}/teacher_errors.png', bbox_inches="tight")
    plt.close()

def drawStudentVsTeacher(studentModelName, testInputs, testOutputs, outputDir, linearShift_m, linearShift_b):
    teacherModel = keras.models.load_model("models/teacher")
    studentModel = keras.models.load_model(f"models/{studentModelName}")

    #studentTargets = makeStudentTargets(testInputs, testOutputs, teacherModel)
    currentTargets = teacherModel.predict(
        testInputs,
        verbose=0
    )
    currentTargets = tf.reshape(currentTargets, [-1,18,14])
    currentTargets = tf.math.reduce_mean((currentTargets-testOutputs)**2, axis=[1,2])
    studentTargets = linearShiftTargets(currentTargets, linearShift_m, linearShift_b)

    studentPredictions = studentModel.predict(testInputs, verbose=0)
    studentPredictions = studentPredictions.reshape((studentPredictions.shape[0]))

    errors = np.absolute(np.subtract(studentPredictions, studentTargets.numpy()))

    #print(studentTargets.numpy().shape)
    #print(studentPredictions.shape)
    #print(errors.shape)

    plt.scatter(
        studentTargets,
        errors,
    )
    plt.xlabel("Adjusted Teacher Scores")
    plt.ylabel("Student Errors")
    plt.savefig(
        f"{outputDir}/{studentModelName}_Error.png",
        bbox_inches="tight",
    )
    plt.close()

#n=2
def crystal_ball(x, *p):
    alpha, x_bar, sigma = p
    A = np.power((2/np.abs(alpha)), 2) * np.exp(-np.abs(alpha)**2/2)
    B = 2/np.abs(alpha) - np.abs(alpha)
    C = 2/np.abs(alpha) * (1/(2-1))*np.exp(-np.abs(alpha)**2/2)
    D = np.sqrt(np.pi/2)*(1+scipy.special.erf(np.abs(alpha)/np.sqrt(2)))
    N = 1/(sigma*(C+D))

    condition = (x-x_bar)/sigma > -alpha
    gauss_output = np.exp((-(x-x_bar)**2)/(2*(sigma**2)))
    power_law = np.power(A*(B-((x-x_bar)/sigma)), -2)

    return np.where(condition, gauss_output, power_law)

# not strictly normalized to 1, but whatever, it has peak at 1
def gauss(x, *p):
    A, mu, sigma = p
    return A * np.exp((-1/2)*((x-mu)/sigma)**2)

def getTeacherLossPattern(inputs, outputs, teacherModel):
    #teacherModel = keras.models.load_model("models/teacher")
    teacherPredictions = teacherModel.predict(
        inputs,
        verbose=0,
    )
    teacherPredictions = teacherPredictions.reshape(-1, 18, 14)
    mse = np.mean(
        np.subtract(teacherPredictions, outputs)**2,
        axis=(1,2)
    )
    nBins = 40
    amounts, binEdges, _ = plt.hist(
        mse,
        bins=nBins,
    )

    binCenters = (binEdges[:-1]+binEdges[1:])/2

    amplitudeGuess = np.max(amounts)
    centerGuess = binCenters[np.argmax(amounts)]
    sigmaGuess=(binCenters[-1]-binCenters[0])/2

    gaussParameters = [amplitudeGuess, 0.0, 1.0]
    fitCoeff, var_matrix = curve_fit(gauss, binCenters, amounts, p0=gaussParameters)
    plt.close()

    return fitCoeff

def linearShiftTargets(targets, m, b):
    return m*targets + b

def makeStudentTargets(inputs, trueValues, model):
    currentTargets = model.predict(
        inputs,
        verbose=0,
    )
    currentTargets = tf.reshape(currentTargets, [-1,18,14])
    currentTargets = tf.math.reduce_mean((currentTargets-trueValues)**2, axis=[1,2])

    #now we need to rescale to 2^-8-(2^8-2^-8), which is the approximate range of our outputs
    #to do that, new element = ((new max - new min)/(old max - old min)) * old element + ((new min * old max - new max * old min)/(old max - old min))
    #
    oldMax = tf.math.reduce_max(currentTargets)
    oldMin = tf.math.reduce_min(currentTargets)

    newMax = 255.99609375
    newMin = 0.00390625
    
    m = (newMax-newMin)/(oldMax-oldMin)
    b = (newMin*oldMax - newMax*oldMin)/(oldMax - oldMin)

    currentTargets = linearShiftTargets(currentTargets, m, b)

    return currentTargets, m, b

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

    # with h5py.File("/afs/hep.wisc.edu/cms/aloeliger/anomalyTriggerWork/training/2023/Signal/DummyOutliers-Training.h5") as theFile:
    #     trainOutliers = np.array(theFile["CaloRegions"])

    # with h5py.File("/afs/hep.wisc.edu/cms/aloeliger/anomalyTriggerWork/training/2023/Signal/DummyOutliers-Validation.h5") as theFile:
    #     valOutliers = np.array(theFile["CaloRegions"])
    
    # randomInputsTrainLength = math.floor(0.25 * len(theDataset))
    # randomInputsValLength = math.floor(0.05 * len(theDataset))
    
    # trainOutliers = np.random.gamma(
    #     0.001,
    #     size = (randomInputsTrainLength, 18, 14),
    # )
    # valOutliers = np.random.gamma(
    #     0.001,
    #     size = (randomInputsValLength, 18, 14),
    # )

    #console.print(theDataset.shape)
    #console.print(theDataset[:3])
    
    # norm each individual output, and reshape the input
    all_inputData = theDataset.reshape((theDataset.shape[0], 18*14))
    all_outputData = makeNormedInstances(theDataset)

    # trainInputOutliers = trainOutliers.reshape((trainOutliers.shape[0], 18*14))
    # trainOutputOutliers = makeNormedInstances(trainOutliers)

    # valInputOutliers = valOutliers.reshape((valOutliers.shape[0], 18*14))
    # valOutputOutliers = makeNormedInstances(valOutliers)

    trainval_inputData, test_inputData, trainval_outputData,  test_outputData = train_test_split(all_inputData, all_outputData, test_size=0.4, random_state=42)
    inputData, valInput, outputData, valOutput = train_test_split(trainval_inputData, trainval_outputData, test_size=0.1/(0.6), random_state=42)

    print(inputData.shape)
    print(outputData.shape)

    # print(trainInputOutliers.shape)
    # print(trainOutputOutliers.shape)

    # print(valInputOutliers.shape)
    # print(valOutputOutliers.shape)

    # trainInputWithOutliers = np.append(inputData, trainInputOutliers, axis=0)
    # trainOutputWithOutliers = np.append(outputData, trainOutputOutliers, axis=0)

    # valInputWithOutliers = np.append(valInput, valInputOutliers, axis=0)
    # valOutputWithOutliers = np.append(valOutput, valOutputOutliers, axis=0)

    # print(trainInputWithOutliers.shape)
    # print(trainOutputWithOutliers.shape)

    # print(valInputWithOutliers.shape)
    # print(valOutputWithOutliers.shape)

    #console.print(outputData[:3])

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
        metrics = [keras.metrics.MeanAbsoluteError()],
        optimizer=keras.optimizers.Adam(learning_rate=0.001)
    )
    teacherBestModel = keras.callbacks.ModelCheckpoint("models/teacher", save_best_only=True)
    teacherLog = keras.callbacks.CSVLogger(f"models/teacher/training.log", append=True)

    ae_model.summary()

    # CICADA v1
    # inputs = Input(shape=self.input_shape, name="inputs_")                                                                                                                                            
    # x = QDenseBatchnorm(                                                                                                                                                                              
    #     16,                                                                                                                                                                                           
    #     kernel_quantizer=quantized_bits(8, 1, 1, alpha=1.0),                                                                                                                                          
    #     bias_quantizer=quantized_bits(8, 3, 1, alpha=1.0),                                                                                                                                            
    #     name="dense1",                                                                                                                                                                                
    # )(inputs)                                                                                                                                                                                         
    # x = QActivation("quantized_relu(10, 6)", name="relu1")(x)                                                                                                                                         
    # x = Dropout(1 / 8)(x)                                                                                                                                                                             
    # x = QDense(
    #     1,
    #     kernel_quantizer=quantized_bits(12, 3, 1, alpha=1.0),
    #     use_bias=False,
    #     name="dense2",
    # )(x)
    # outputs = QActivation("quantized_relu(16, 8)", name="outputs")(x)
    # return Model(inputs, outputs, name="cicada-v1")
    
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

    #  CICADA v2
    # inputs = Input(shape=self.input_shape, name="inputs_")
    # x = Reshape((18, 14, 1), name="reshape")(inputs)
    # x = QConv2D(
    #     4,
    #     (2, 2),
    #     strides=2,
    #     padding="valid",
    #     use_bias=False,
    #     kernel_quantizer=quantized_bits(12, 3, 1, alpha=1.0),
    #     name="conv",
    # )(x)
    # x = QActivation("quantized_relu(10, 6)", name="relu0")(x)
    # x = Flatten(name="flatten")(x)
    # x = Dropout(1 / 9)(x)
    # x = QDenseBatchnorm(
    #     16,
    #     kernel_quantizer=quantized_bits(8, 1, 1, alpha=1.0),
    #     bias_quantizer=quantized_bits(8, 3, 1, alpha=1.0),
    #     name="dense1",
    # )(x)
    # x = QActivation("quantized_relu(10, 6)", name="relu1")(x)
    # x = Dropout(1 / 8)(x)
    # x = QDense(
    #     1,
    #     kernel_quantizer=quantized_bits(12, 3, 1, alpha=1.0),
    #     use_bias=False,
    #     name="dense2",
    # )(x)
    # outputs = QActivation("quantized_relu(16, 8)", name="outputs")(x)
    # return Model(inputs, outputs, name="cicada-v2")
    
    cicada_v2 = keras.models.Sequential([
        keras.layers.Input(shape=inputData.shape[1:]),
        keras.layers.Reshape((18,14,1)),
        keras.layers.LayerNormalization(axis=1),
        QConv2D(
            4,
            (2, 2),
            strides=2,
            padding="valid",
            use_bias=False,
            kernel_quantizer=quantized_bits(12, 3, 1, alpha=1.0),
        ),
        QActivation("quantized_relu(10,6)"),
        keras.layers.Flatten(),
        keras.layers.Dropout(1 / 9) ,
        QDense(
            16,
            kernel_quantizer=quantized_bits(8, 1, 1, alpha=1.0), 
            bias_quantizer = quantized_bits(8, 3, 1, alpha=1.0),
        ),
        QActivation("quantized_relu(10, 6)"),
        keras.layers.Dropout(1 / 8),
        QDense(
            1,
            kernel_quantizer = quantized_bits(12, 3, 1, alpha = 1.0),
            use_bias=False,
        ),
        QActivation("quantized_relu(16, 8)"),
    ])
    cicada_v2.compile(
        loss='mae',
        weighted_metrics = [keras.metrics.MeanAbsolutePercentageError()],
        optimizer=keras.optimizers.Adam(learning_rate=0.001)
    )
    cicada_v2_BestModel = keras.callbacks.ModelCheckpoint("models/cicada_v2", save_best_only=True)
    cicada_v2_Log = keras.callbacks.CSVLogger(f"models/cicada_v2/training.log", append=True)
    cicada_v2_nan = keras.callbacks.TerminateOnNaN()
    
    cicada_v2.summary()
    
    numEpochs = 1
    studentEpochsPer = 1
    totalStudentEpochs = numEpochs * studentEpochsPer

    console.rule("Teacher Training")
    ae_model.fit(
        x=inputData,
        y=outputData,
        validation_data=(valInput, valOutput),
        epochs=numEpochs,
        callbacks=[teacherBestModel, teacherLog]
    )
    console.rule()

    console.log("Making student weights...")
    best_teacher = keras.models.load_model("models/teacher")
    gaussParameters = getTeacherLossPattern(inputData, outputData, best_teacher)
    
    teacherPredictions = best_teacher.predict(inputData, verbose=0)
    teacherPredictions = teacherPredictions.reshape(-1, 18, 14)
    mse = np.mean(
        np.subtract(teacherPredictions, outputData)**2,
        axis=(1,2),
    )
    valPredictions = best_teacher.predict(valInput, verbose=0)
    valPredictions = valPredictions.reshape(-1, 18, 14)
    valMse = np.mean(
        np.subtract(valPredictions, valOutput)**2,
        axis=(1,2),
    )

    weightGenerator = lambda x: 1.0/gauss(x, 1.0, gaussParameters[1], gaussParameters[2])
    trainWeights = weightGenerator(mse)
    valWeights = weightGenerator(valMse)
    #renormalize the weights
    trainWeights = trainWeights * (len(trainWeights)/np.sum(trainWeights))
    valWeights = valWeights * (len(valWeights)/np.sum(valWeights))

    console.log("Making student targets...")
    studentTargets, linearShift_m, linearShift_b = makeStudentTargets(inputData, outputData, best_teacher)
    console.log(f"Linear shift slope: {linearShift_m}")
    console.log(f"Linear shift bias: {linearShift_b}")
    teacher_val_predictions = best_teacher.predict(valInput, verbose=0)
    teacher_val_predictions = tf.reshape(teacher_val_predictions, [-1, 18, 14])
    teacher_val_predictions = tf.math.reduce_mean((teacher_val_predictions - valOutput)**2, axis=[1,2])
    valStudentTargets = linearShiftTargets(teacher_val_predictions, linearShift_m, linearShift_b)

    console.rule("CICADA v1")
    cicada_v1.fit(
        x=inputData,
        y=studentTargets,
        sample_weight=trainWeights,
        epochs=totalStudentEpochs,
        validation_data=(valInput, valStudentTargets, valWeights),
        callbacks=[cicada_v1_BestModel, cicada_v1_Log, cicada_v1_nan],
    )

    console.rule("CICADA v2")
    cicada_v1.fit(
        x=inputData,
        y=studentTargets,
        sample_weight=trainWeights,
        epochs=totalStudentEpochs,
        validation_data=(valInput, valStudentTargets, valWeights),
        callbacks=[cicada_v2_BestModel, cicada_v2_Log, cicada_v2_nan],
    )
    console.rule()
    console.print()

    printable_test_inputs = test_inputData[:20]
    printable_test_outputs = test_outputData[:20]
    console.print("Testable inputs")
    console.print(makeNormedInstances(printable_test_inputs.reshape(-1,18,14)))
    console.print("Testable outputs")
    console.print(printable_test_outputs)
    console.print("Teacher predictions")
    teacher_printable_outputs = ae_model.predict(printable_test_inputs)
    teacher_printable_outputs = teacher_printable_outputs.reshape(-1, 18, 14)
    console.print(teacher_printable_outputs)
    teacher_errors = np.mean(
        np.subtract(teacher_printable_outputs, printable_test_outputs.reshape(-1,18,14))**2,
        axis=(1,2),
    )
    console.print("Teacher errors:")
    console.print(teacher_errors)
    console.print("Student Weights:")
    student_printable_weights = weightGenerator(teacher_errors)
    console.print(student_printable_weights)
    console.print("Student Targets:")
    student_printable_targets = linearShiftTargets(teacher_errors, linearShift_m, linearShift_b)
    console.print(student_printable_targets)
    console.print("CICADA V1 Predictions:")
    cicada_v1 = keras.models.load_model(f"models/cicada_v1")
    cicada_v1_printable_outputs = cicada_v1.predict(printable_test_inputs)
    console.print(cicada_v1_printable_outputs)
    console.print("CICADA V2 Predictions:")
    cicada_v2 = keras.models.load_model(f"models/cicada_v2")
    cicada_v2_printable_outputs = cicada_v2.predict(printable_test_inputs)
    console.print(cicada_v2_printable_outputs)
        
    plotOutputDir = Path("plots")
    plotOutputDir.mkdir(parents=True, exist_ok=True)
    for modelName in ("teacher", "cicada_v1", "cicada_v2"):
        drawLossHistory(modelName, outputDir=plotOutputDir)

    drawTeacherErrors(
        testInputs = test_inputData,
        testOutputs = test_outputData,
        outputDir = plotOutputDir,
    )

    for modelName in ("cicada_v1", "cicada_v2"):
        drawStudentVsTeacher(
            modelName,
            testInputs = test_inputData,
            testOutputs = test_outputData,
            outputDir = plotOutputDir,
            linearShift_m = linearShift_m,
            linearShift_b = linearShift_b,
        )

if __name__ == '__main__':
    main()

#!/usr/bin/env bash
VERSION=2

NFS_LOCATION="/nfs_scratch/aloeliger/Ztoee_wminiCICADA/v_${VERSION}/test/"
DAGS_LOCATION="${NFS_LOCATION}/dags/"
SUBMIT_LOCATION="${NFS_LOCATION}/submit/"
OUTPUT_DIR="/hdfs/store/user/aloeliger/Ztoee_wminiCICADA/v_${VERSION}/DY/"
INPUT_FILES="$CMSSW_BASE/src/anomalyDetection/ZtoeePeakAnalysis/metaData/testFile.txt"
CONFIG="$CMSSW_BASE/src/anomalyDetection/ZtoeePeakAnalysis/python/ntuplize.py"

mkdir -p ${DAGS_LOCATION}

farmoutAnalysisJobs \
    --infer-cmssw-path \
    --submit-dir="${SUBMIT_LOCATION}" \
    --output-dag-file="${DAGS_LOCATION}/dag" \
    --output-dir="${OUTPUT_DIR}" \
    --input-files-per-job=1 \
    --input-file-list="${INPUT_FILES}" \
    --assume-input-files-exist \
    --use-singularity="CentOS7" \
    --input-dir=/ \
    "Ztoee_wminiCICADA_test_v_${version}" "${CONFIG}" 'outputFile=$outputFileName' 'inputFiles=$inputFileNames'
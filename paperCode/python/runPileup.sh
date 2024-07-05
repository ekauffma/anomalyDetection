#!/bin/bash

# Get the number of lines in each file
lines_file1=$(wc -l < paperCode/python/primaryInputFiles.txt)
lines_file2=$(wc -l < paperCode/python/secondaryInputFiles.txt)

# Ensure both files have the same number of lines
if [ "$lines_file1" -ne "$lines_file2" ]; then
    echo "Files have a different number of lines."
    exit 1
fi

i=1

# Read lines from both files and run the program
paste paperCode/python/primaryInputFiles.txt paperCode/python/secondaryInputFiles.txt | while IFS=$'\t' read -r line1 line2; do
    output_file="output_${i}.root"
    cmsRun paperCode/python/makeCICADANtuplesFromRAW_withNPV.py  primaryInputFile="$line1" secondaryInputFile="$line2" outputFile="$output_file"
    i=$((i+1))
done

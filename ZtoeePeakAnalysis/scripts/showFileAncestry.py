#!/usr/bin/env python3

import subprocess
import argparse

def getListOfAncestors(fileName: str):
    dasQuery = f"dasgoclient --query=\"parent file={fileName}\""
    queryProcess = subprocess.run(
        [dasQuery],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    resultString = queryProcess.stdout.decode()

    fileList = resultString.split('\n')
    fileList.remove('')

    return fileList

def printAncestors(fileName: str, indentationLevel: int = 1):
    theAncestors = getListOfAncestors(fileName)
    if theAncestors == []: #we're done here
        return
    for ancestor in theAncestors:
        printStr = indentationLevel*"\t"+f"\u2192 {ancestor}"
        print(printStr)
        printAncestors(ancestor, indentationLevel+1)


def main(args):
    print(f'{args.fileName}')
    printAncestors(args.fileName)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Utility for showing all ancestors of a DAS file')
    argparser.add_argument('fileName',nargs='?',help='name of the file to query in das')

    args = argparser.parse_args()

    main(args)
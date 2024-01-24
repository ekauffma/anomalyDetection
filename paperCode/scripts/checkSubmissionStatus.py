import argparse
import os
from rich.console import Console
from rich.table import Table
import subprocess

console = Console()

def main(args):
    #let's start by getting a list of directories available at the directory location
    directoryItems = os.listdir(args.directoryLocation)
    directories = [os.path.join(args.directoryLocation, item) for item in directoryItems if os.path.isdir(os.path.join(args.directoryLocation, item))]

    dateDirectories = [item for item in directories if args.datetime in item]

    # console.print(dateDirectories)
    for directory in dateDirectories:
        console.rule(directory)
        statusCommand = f'crab status -d {directory}/crab/crab_Paper_Ntuples_{args.datetime}'
        if args.kill:
            statusCommand = f'crab kill -d {directory}/crab/crab_Paper_Ntuples_{args.datetime}'
        console.print(f'Command:\n{statusCommand}')
        subprocess.run(
            [statusCommand],
            shell=True,
        )
        console.rule()
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check a specific day\'s submission status')
    parser.add_argument(
        '-d',
        '--directoryLocation',
        required=True,
        nargs='?',
        help='Directory containing the submit directories',
    )
    parser.add_argument(
        '--datetime',
        required=True,
        nargs='?',
        help='The date of submissions to check. Format is DDMMMYY, where D is a (zero-padded) day num, MMM is a month abbreviation (e.g. Jun or Feb) and YY is the last two year digits'
    )
    parser.add_argument(
        '--kill',
        action='store_true',
        help='Instead of reading the status, kill everything with the given datetime'
    )

    args = parser.parse_args()

    main(args)
#!/usr/bin/env pyhthon3
import h5py
import argparse

def main(args):
    for fileName in args.hdf5Files:
            with h5py.File(fileName) as theFile:
                for dataset_name in theFile.keys():
                     print(dataset_name)
                     print(f'\tAttributes: {theFile[dataset_name].attrs}')
                     print(f'\tShape: {theFile[dataset_name].shape}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Dump the contents of an HDF5 file out")
    parser.add_argument('hdf5Files', nargs='+', help='Files to dump the contents of')

    args = parser.parse_args()

    main(args)
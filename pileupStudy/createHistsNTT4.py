########################################################################
## createHistsPileup.py                                               ##
## Author: Elliott Kauffman                                           ##
## make score and rate histograms for CICADA                          ##
########################################################################

import ROOT
import argparse
import numpy as np
from paperSampleBuilder import samples
import json

RATE_VAL = 3.0 # kHz

def main(outfile):

    # get zerobias and filter out training events
    zero_bias = samples['ZeroBias'].getNewDataframe()

    # minimum and maximum number of vertices for histogram
    min_vtx = 0.0
    max_vtx = 50.0

    # create ROOT file for hists
    output_file = ROOT.TFile(outfile, "RECREATE")

    # define towers to count for NTT4 (used as approximation of pileup)
    zero_bias = zero_bias.Define("goodTowers_iet",
                                 "iet[abs(ieta) <= 4]",
                                 {"L1CaloTower/iet", "L1CaloTower/ieta"})

    hist = ROOT.TH1F("NTT4", "NTT4", int(max_vtx-min_vtx), min_vtx/5, max_vtx/5)

    for j in range(int(min_vtx), int(max_vtx)):

        print("    nPV = ", j)


        # filter zerobias for current pileup (NTT4) and count events
        current_count = zero_bias.Filter(f"Sum(goodTowers_iet>1)=={j}").Count().GetValue()
        print("        current_count = ", current_count)

        # add to histogram
        hist.SetBinContent(j+1, current_count)

    hist.Write()

    output_file.Write()
    output_file.Close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-o",
        "--outfile",
        help="file to save histograms to")

    args = parser.parse_args()

    main(args.outfile)

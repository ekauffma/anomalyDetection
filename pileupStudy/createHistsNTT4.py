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
import awkward as ak

RATE_VAL = 3.0 # kHz

def main(outfile):

    # get zerobias and filter out training events
    zero_bias = samples['ZeroBias'].getNewDataframe(["l1CaloTowerTree/L1CaloTowerTree"])

    branches = ["L1CaloTower.iet", "L1CaloTower.ieta", "L1CaloTower.iphi"]

    ak_array = ak.from_rdataframe(zero_bias, columns=branches)

    # minimum and maximum number of vertices for histogram
    min_vtx = 0.0
    max_vtx = 50.0

    # create file for zerobias hists
    output_file = ROOT.TFile(outfile, "RECREATE")

    ak_array = ak_array[(abs(ak_array["L1CaloTower.ieta"])<=4)]
    ak_array = ak_array.drop(["L1CaloTower.ieta", "L1CaloTower.iphi"], axis=1)
    ak_array = ak_array.groupby(["event"]).count()
    ak_array = ak_array.rename(columns={"L1CaloTower.iet": "ntt4"})
    ak_array["ntt4"] /= 5
    ak_array["ntt4"] = ak_array["ntt4"].round()
    ak_array["ntt4"] = ak_array["ntt4"].clip(upper=32)

    histModel = ROOT.RDF.TH1DModel(
        "ntt4",
        "NTT4",
        int(max_vtx-min_vtx),
        int(min_vtx),
        int(max_vtx)
    )
    ntt4Hist = df.Histo1D(histModel, "NTT4")
    ntt4Hist.Write()

    output_file.Write()
    output_file.Close()

    f.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-o",
        "--outfile",
        help="file to save histograms to")

    args = parser.parse_args()

    main(args.outfile)

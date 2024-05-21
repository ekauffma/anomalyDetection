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

def main():

    # load json containing CICADA rates
    f = open('paperCode/metadata/rateTables.json')
    rateTables = json.load(f)

    # get list of sample names and remove ZeroBias
    sample_names = list(samples.keys())
    if 'ZeroBias' in sample_names:
        sample_names.remove('ZeroBias')

    # get zerobias and filter out training events
    zero_bias = samples['ZeroBias'].getNewDataframe()
    zero_bias = zero_bias.Filter('lumi % 2 == 1')

    # names of CICADA models
    cicada_names = ["CICADA_v1p2p2",
                    "CICADA_v2p2p2",
                    "CICADA_v1p2p2N",
                    "CICADA_v2p2p2N"]

    # minimum and maximum CICADA score for score histogram
    min_score_cicada = 0.0
    max_score_cicada = 256.0
    nBins = int(max_score_cicada-min_score_cicada)

    # minimum and maximum number of vertices for histogram
    min_vtx = 0.0
    max_vtx = 100.0

    # create file for zerobias hists
    output_file = ROOT.TFile("hists_pileup_240514.root", "RECREATE")

    # define towers to count for NTT4 (used as approximation of pileup)
    zero_bias = zero_bias.Define("goodTowers_et",
                                 "et[abs(eta) <= 4]",
                                 {"L1CaloTower/et", "L1CaloTower/eta"})

    # create and fill CICADA score histograms for zerobias
    for i in range(len(cicada_names)):
        print("CICADA VERSION: ", cicada_names[i])

        ratedata = rateTables[f"{cicada_names[i]}_score"]
        rate_vals = np.array(list(ratedata.values()))
        idx = (np.abs(rate_vals - RATE_VAL)).argmin()
        thresh = list(ratedata.keys())[idx]

        scoreHistModel = ROOT.RDF.TH1DModel(
            f"anomalyScore_ZeroBias_{cicada_names[i]}",
            f"anomalyScore_ZeroBias_{cicada_names[i]}",
            nBins,
            min_score_cicada,
            max_score_cicada
        )

        rateHist = ROOT.TH1F(f"rateHist_{cicada_names[i]}", ";nPV;Rate [kHz]", int(max_vtx-min_vtx), int(min_vtx), int(max_vtx))

        for j in range(int(min_vtx), int(max_vtx)):

            print("    nPV = ", j)

            # filter zerobias for current pileup (NTT4) and create score hist
            zero_bias_current = zero_bias.Filter(f"Sum(goodTowers_et>0.5)=={j}")
            scoreHist = zero_bias_current.Histo1D(scoreHistModel, f"{cicada_names[i]}_score")

            # calculate efficiency
            total_integral = float(scoreHist.Integral())
            partial_integral = float(scoreHist.Integral(int(idx), int(scoreHist.GetNbinsX())))
            if total_integral!=0:
                uncertainty = np.sqrt(partial_integral)/total_integral
                partial_integral = partial_integral/total_integral
            else:
                uncertainty = 0
                partial_integral = 0

            # set in histogram
            rateHist.SetBinContent(j+1, partial_integral)
            rateHist.SetBinError(j+1, uncertainty)

        # convert values in histogram to rates
        rateHist.Scale(2544.0 * 11245e-3)

        # write the histogram to file
        rateHist.Write()

    output_file.Write()
    output_file.Close()

    f.close()

if __name__ == "__main__":

	main()

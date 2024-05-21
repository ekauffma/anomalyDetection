import ROOT
import argparse
import numpy as np
from paperSampleBuilder import samples

cicada_names = ["CICADA_v1p2p2",
                "CICADA_v2p2p2",
                "CICADA_v1p2p2N",
                "CICADA_v2p2p2N"]


def main(input_file, output_dir):

    f = ROOT.TFile(input_file)

    for i in range(len(cicada_names)):


        hist = f.Get(f"rateHist_{cicada_names[i]}")

        c1 = ROOT.TCanvas("c1", "Anomaly Score", 1000,600)
        hist.SetMarkerColor(4)
        hist.SetMarkerStyle(20)
        hist.SetStats(0)
        hist.SetTitle("")

		#hist.GetYaxis().SetRangeUser(1,1e9)
		#hist.GetXaxis().SetRangeUser(0,256)

        hist.Draw("PE")

        c1.SetLogy()
        c1.Draw()
        c1.SaveAs(f"{output_dir}/pileup_{cicada_names[i]}.png")
        c1.Close()

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="This program creates CICADA score plots")
	parser.add_argument("-i", "--input_file", help="path to input ROOT file containing hists")
	parser.add_argument("-o", "--output_dir", default='./', help="directory to save output plots")

	args = parser.parse_args()

	main(args.input_file, args.output_dir)

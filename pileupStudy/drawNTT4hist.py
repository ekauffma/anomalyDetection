import ROOT
import argparse
import numpy as np
from paperSampleBuilder import samples


def main(output_dir):

    f = ROOT.TFile("ntt4hist.root")

    hist = f.Get("NTT4")


    c1 = ROOT.TCanvas("c1", "NTT4", 1000,600)
    hist.SetMarkerColor(4)
    hist.SetMarkerStyle(20)
    hist.GetXaxis().SetTitle("NTT4");
    hist.GetYaxis().SetTitle("Counts");
    hist.SetStats(0)
    hist.SetTitle("")

    #hist.GetYaxis().SetRangeUser(1,1e9)
    #hist.GetXaxis().SetRangeUser(0,256)
    hist.Draw("e")

    c1.SetLogy()
    c1.Draw()
    c1.SaveAs(f"{output_dir}/NTT4hist.png")
    c1.Close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This program creates NTT4 plots")
    parser.add_argument("-o", "--output_dir", default='./', help="directory to save output plots")

    args = parser.parse_args()
    main(args.output_dir)

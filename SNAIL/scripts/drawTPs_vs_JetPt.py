import ROOT
import argparse

def drawHist(theHist, xAxisTitle, savePath):
    #need to properly set the errors here.
    theHist.SetMarkerStyle(20)
    theHist.SetLineColor(ROOT.kBlack)

    theCanvas = ROOT.TCanvas("average")

    theHist.Draw("E1")

    theHist.SetTitle("")
    theHist.GetXaxis().SetTitle(xAxisTitle)
    theHist.GetYaxis().SetTitle("Average Matched Puppi - Trigger Jet p_{T}")

    cmsLatex = ROOT.TLatex()
    cmsLatex.SetTextSize(0.05)
    cmsLatex.SetNDC(True)
    cmsLatex.SetTextAlign(32)
    cmsLatex.DrawLatex(0.9,0.92, "#font[61]{CMS} #font[52]{Preliminary}")
    
    theCanvas.SaveAs(savePath)

def main(args):
    ROOT.gStyle.SetOptStat(0)
    theFile = ROOT.TFile(args.inputFile)
    
    nTPHist = theFile.Get("AverageJetEnergyDelta")
    drawHist(nTPHist, "# of HCAL + ECAL TPs", "AverageMatchedPairDelta.png")
    
    tpEtHist = theFile.Get("AverageJetEnergyDelta_TPET")
    drawHist(tpEtHist, "Total HCAL+ECAL TP E_{T}", "AverageMatchedPairDelta_TPET.png")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Draw the makeTPs_vs_JetPt.py script")

    parser.add_argument(
        '--inputFile',
        '-i',
        required=True,
        nargs='?',
        help="File from the output",
    )

    args = parser.parse_args()
    
    main(args)

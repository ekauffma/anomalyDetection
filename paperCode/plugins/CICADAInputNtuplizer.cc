// system include files
#include <memory>
#include <iostream>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/ServiceRegistry/interface/Service.h"

#include "DataFormats/L1CaloTrigger/interface/L1CaloCollections.h"
#include "DataFormats/L1CaloTrigger/interface/L1CaloRegion.h"

#include "TTree.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include <string>

class CICADAInputNtuplizer : public edm::one::EDAnalyzer< edm::one::SharedResources >
{
    public:
        explicit CICADAInputNtuplizer(const edm::ParameterSet&);
        ~CICADAInputNtuplizer() override = default;

    private:
        void beginJob() override {};
        void analyze(const edm::Event&, const edm::EventSetup&) override;
        void endJob() override {};

        edm::EDGetTokenT<L1CaloRegionCollection> regionsToken;
        int modelInput[18][14];
        unsigned short int tauBits[18][14];
        unsigned short int egBits[18][14];

        edm::Service<TFileService> theFileService;
        TTree* triggerTree;
};

CICADAInputNtuplizer::CICADAInputNtuplizer(const edm::ParameterSet& iConfig):
 regionsToken(consumes<L1CaloRegionCollection>(iConfig.getParameter<edm::InputTag>("emuRegionsToken")))
{
    usesResource("TFileService");
    triggerTree = theFileService->make< TTree >("CICADAInputTree","(emulator) region information");
    triggerTree -> Branch("modelInput", &modelInput, "modelInput[18][14]/s");
    triggerTree -> Branch("tauBits", &tauBits, "tauBits[18][14]/O");
    triggerTree -> Branch("egBits", &egBits, "tauBits[18][14]/O");
}

void CICADAInputNtuplizer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    edm::Handle<std::vector<L1CaloRegion>> emuRegions;
    iEvent.getByToken(regionsToken, emuRegions);
    for(const L1CaloRegion& theRegion: *emuRegions)
    {
      tauBits[theRegion.gctPhi()][theRegion.gctEta()-4] = (unsigned short int) theRegion.tauVeto();
      egBits[theRegion.gctPhi()][theRegion.gctEta()-4] = (unsigned short int) theRegion.overFlow();
        modelInput[theRegion.gctPhi()][theRegion.gctEta()-4] = theRegion.et();
    }
    triggerTree->Fill();
}

DEFINE_FWK_MODULE(CICADAInputNtuplizer);

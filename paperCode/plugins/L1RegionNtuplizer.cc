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

#include "DataFormats/EcalDigi/interface/EcalDigiCollections.h"
#include "DataFormats/HcalDigi/interface/HcalDigiCollections.h"
#include "DataFormats/L1CaloTrigger/interface/L1CaloCollections.h"
#include "DataFormats/L1CaloTrigger/interface/L1CaloRegion.h"

#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "TTree.h"

#include <string>

class L1RegionNtuplizer : public edm::one::EDAnalyzer<edm::one::SharedResources>
{
    public:
        explicit L1RegionNtuplizer(const edm::ParameterSet&);
        ~L1RegionNtuplizer() override = default;

    private:
        void beginJob() override {};
        void analyze(const edm::Event&, const edm::EventSetup&) override;
        void endJob() override {};

        edm::EDGetTokenT< L1CaloRegionCollection > regionSource;
        unsigned int regionEt[18][14];

        edm::Service<TFileService> theFileService;
        TTree* triggerTree;
};

L1RegionNtuplizer::L1RegionNtuplizer(const edm::ParameterSet& iConfig):
    regionSource(consumes<L1CaloRegionCollection>(iConfig.getParameter<edm::InputTag>("regionToken")))
{
    usesResource("TFileService");

    triggerTree = theFileService->make<TTree>("L1EmuRegions", "(emulator) L1Calo Region information");
    triggerTree -> Branch("regionEt", &regionEt, "regionEt[18][14]/i");
}

void L1RegionNtuplizer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;

    Handle<L1CaloRegionCollection> emuRegions;
    iEvent.getByToken(regionSource, emuRegions);

    for(const L1CaloRegion& theRegion: *emuRegions)
    {
        regionEt[theRegion.gctPhi()][theRegion.gctEta()-4] = theRegion.et();
    }

    triggerTree->Fill();
}

DEFINE_FWK_MODULE(L1RegionNtuplizer);

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

#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "TTree.h"

#include "DataFormats/PatCandidates/interface/Jet.h"

class jetNtuplizer: public edm::one::EDAnalyzer< edm::one::SharedResources>
{
    public:
        explicit jetNtuplizer(const edm::ParameterSet&);
        ~jetNtuplizer() override = default;

    private:
        void beginJob() override {};
        void endJob() override {};

        void analyze(const edm::Event&, const edm::EventSetup&) override;

        edm::EDGetTokenT<std::vector<pat::Jet>> objectSrc;
        edm::Service<TFileService> theFileService;

        TTree* outputTree;
        unsigned int nObjects = 0;
        std::vector<double> ptVector;
        std::vector<double> etaVector;
        std::vector<double> phiVector;
        std::vector<double> massVector;
        std::vector<double> etVector;
        std::vector<int> chargeVector;
        std::vector<double> mtVector;
        std::vector<double> vxVector;
        std::vector<double> vyVector;
        std::vector<double> vzVector;
        std::vector<size_t> numberOfDaughtersVector;
        std::vector<double> vertexChi2Vector;
};

jetNtuplizer::jetNtuplizer(const edm::ParameterSet& iConfig):
    objectSrc(consumes<std::vector<pat::Jet>>(iConfig.getParameter<edm::InputTag>("objectSrc")))
{
    usesResource("TFileService");
    
    outputTree = theFileService->make<TTree>("PuppiJets", "Jet Information");
    outputTree->Branch("nObjects", &nObjects);
    outputTree->Branch("ptVector", &ptVector);
    outputTree->Branch("etaVector", &etaVector);
    outputTree->Branch("phiVector", &phiVector);
    outputTree->Branch("massVector", &massVector);
    outputTree->Branch("etVector", &etVector);
    outputTree->Branch("chargeVector", &chargeVector);
    outputTree->Branch("mtVector", &mtVector);
    outputTree->Branch("vxVector", &vxVector);
    outputTree->Branch("vyVector", &vyVector);
    outputTree->Branch("vzVector", &vzVector);
    outputTree->Branch("nDaughters", &numberOfDaughtersVector);
    outputTree->Branch("vertexChi2Vector", &vertexChi2Vector);
}

void jetNtuplizer::analyze(const edm::Event& iEvent,const edm::EventSetup& iSetup)
{
    edm::Handle<std::vector<pat::Jet>> jetHandle;
    iEvent.getByToken(objectSrc, jetHandle);

    nObjects = jetHandle->size();

    for(
        auto theObject = jetHandle->begin();
        theObject != jetHandle->end();
        ++theObject
    )
    {
        ptVector.push_back(theObject->pt());
        etaVector.push_back(theObject->eta());
        phiVector.push_back(theObject->phi());
        massVector.push_back(theObject->mass());
        etVector.push_back(theObject->et());
        chargeVector.push_back(theObject->charge());
        mtVector.push_back(theObject->mt());
        vxVector.push_back(theObject->vx());
        vyVector.push_back(theObject->vy());
        vzVector.push_back(theObject->vz());
        // dxyVector.push_back(theObject->dxy());
        // dzVector.push_back(theObject->dz());
        numberOfDaughtersVector.push_back(theObject->numberOfDaughters());
        vertexChi2Vector.push_back(theObject->vertexChi2());
    }

    outputTree->Fill();

    nObjects = 0;
    ptVector.clear();
    etaVector.clear();
    phiVector.clear();
    massVector.clear();
    etVector.clear();     
    chargeVector.clear();
    mtVector.clear();
    vxVector.clear();
    vyVector.clear();
    vzVector.clear();
    // dxyVector.clear();
    // dzVector.clear();
    numberOfDaughtersVector.clear();
    vertexChi2Vector.clear(); 
}

DEFINE_FWK_MODULE(jetNtuplizer);

#include <memory>
#include <iostream>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/ServiceRegistry/interface/Service.h"

#include "DataFormats/VertexReco/interface/Vertex.h"

#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "TTree.h"

class PUVertexNtuplizer : public edm::one::EDAnalyzer< edm::one::SharedResources >
{
    public:
        explicit PUVertexNtuplizer(const edm::ParameterSet&);
        ~PUVertexNtuplizer() override = default;

    private:
        void beginJob() override {};
        void analyze(const edm::Event&, const edm::EventSetup&) override;
        void endJob() override {};

        edm::EDGetTokenT<std::vector<reco::Vertex>> vertexToken;

        edm::Service<TFileService> theFileService;
        TTree* triggerTree;
        int npv = 0;
};

PUVertexNtuplizer::PUVertexNtuplizer(const edm::ParameterSet& iConfig):
    vertexToken( consumes<std::vector<reco::Vertex>>(iConfig.getParameter<edm::InputTag>("pvSrc")))
{
    usesResource("TFileService");

    triggerTree = theFileService -> make<TTree>("PUVertexNtuple", "Quick tree for primary vertices");
    triggerTree -> Branch("npv", &npv);   
}

void PUVertexNtuplizer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;

    Handle<std::vector<reco::Vertex>> vertexHandle;
    iEvent.getByToken(vertexToken, vertexHandle);

    npv = vertexHandle->size();

    triggerTree->Fill();
}

DEFINE_FWK_MODULE(PUVertexNtuplizer);

#include <memory>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "DataFormats/PatCandidates/interface/Electron.h"

#include <TTree.h>
#include <string>

class electronInformationAnalyzer : public edm::one::EDAnalyzer<edm::one::SharedResources> {
    public:
        explicit electronInformationAnalyzer(const edm::ParameterSet&);
        ~electronInformationAnalyzer();

        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

    private:
        virtual void beginJob() override;
        virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
        virtual void endJob() override;

        void fillElectronVectors(const std::vector<pat::Electron> & );
        void clearElectronVectors();

        TTree* theTree;
        edm::Service<TFileService> theFileService;
        edm::EDGetTokenT<std::vector<pat::Electron>> electronToken;

        unsigned int nElectrons = 0;
        std::vector<double> ptVector;
        std::vector<double> etaVector;
        std::vector<double> phiVector;
        std::vector<double> massVector;
        std::vector<int> chargeVector;
};

electronInformationAnalyzer::electronInformationAnalyzer(const edm::ParameterSet& iConfig)
{
    electronToken = consumes<std::vector<pat::Electron>>(iConfig.getParameter<edm::InputTag>("electronSource"));

    usesResource("TFileService");

    theTree = theFileService->make<TTree>("ElectronInformation", "List of all slimmed electrons, and relevant information");
    theTree->Branch("nElectrons", &nElectrons);
    theTree->Branch("ptVector", &ptVector);
    theTree->Branch("etaVector", &etaVector);
    theTree->Branch("phiVector", &phiVector);
    theTree->Branch("massVector", &massVector);
    theTree->Branch("chargeVector", &chargeVector);
}

electronInformationAnalyzer::~electronInformationAnalyzer()
{

}

void electronInformationAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions)
{
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

void electronInformationAnalyzer::beginJob()
{

}

void electronInformationAnalyzer::endJob()
{

}

void electronInformationAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;
    edm::Handle<std::vector<pat::Electron>> electronHandle;
    iEvent.getByToken(electronToken, electronHandle);

    this->clearElectronVectors();
    this->fillElectronVectors(*electronHandle);

    theTree->Fill();
}

void electronInformationAnalyzer::fillElectronVectors(const std::vector<pat::Electron> & electronVector)
{
    for (auto electron = electronVector.begin();
    electron != electronVector.end();
    electron++)
    {
        nElectrons++;
        ptVector.push_back(electron->pt());
        etaVector.push_back(electron->eta());
        phiVector.push_back(electron->phi());
        massVector.push_back(electron->mass());
        chargeVector.push_back(electron->charge());
    }
}

void electronInformationAnalyzer::clearElectronVectors()
{
    nElectrons = 0;
    ptVector.clear();
    etaVector.clear();
    phiVector.clear();
    massVector.clear();
    chargeVector.clear();
}

DEFINE_FWK_MODULE(electronInformationAnalyzer);
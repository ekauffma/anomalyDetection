// Class for creating a neural network score tree for given models
// to be attached to file trees for processing

#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/Utilities/interface/InputTag.h"

#include "FWCore/ServiceRegistry/interface/Service.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "DataFormats/L1CaloTrigger/interface/L1CaloRegion.h"
#include "DataFormats/L1CaloTrigger/interface/L1CaloCollections.h"

#include "PhysicsTools/TensorFlow/interface/TensorFlow.h"

#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "TTree.h"
#include <string>

class kerasCICADAModelNtuplizer : public edm::one::EDAnalyzer< edm::one::SharedResources >
{
public:
  explicit kerasCICADAModelNtuplizer(const edm::ParameterSet&);
  ~kerasCICADAModelNtuplizer() override;

private:
  void beginJob() override {};
  void analyze(const edm::Event&, const edm::EventSetup&) override;
  void endJob() override {};

  const edm::EDGetTokenT<L1CaloRegionCollection> emuRegionsToken;

  tensorflow::Options options;
  tensorflow::MetaGraphDef* metaGraph;
  tensorflow::Session* session;

  std::string branchName;
  std::string treeName;
  float modelOutput;

  edm::Service<TFileService> theFileService;  
  TTree* triggerTree;

};

kerasCICADAModelNtuplizer::kerasCICADAModelNtuplizer(const edm::ParameterSet& iConfig):
  emuRegionsToken(consumes<L1CaloRegionCollection>(iConfig.getUntrackedParameter<edm::InputTag>("regionToken"))),
  branchName(iConfig.getParameter<std::string>("branchName")),
  treeName(iConfig.getParameter<std::string>("treeName"))
{
  usesResource("TFileService");

  std::string fullPathToModel(std::getenv("CMSSW_BASE"));
  fullPathToModel.append(iConfig.getParameter<std::string>("modelLocation"));

  triggerTree = theFileService->make<TTree>(treeName.c_str(), "keras model output");
  triggerTree->Branch(branchName.c_str(), &modelOutput);

  metaGraph = tensorflow::loadMetaGraphDef(fullPathToModel);
  session = tensorflow::createSession(metaGraph, fullPathToModel, options);
}

kerasCICADAModelNtuplizer::~kerasCICADAModelNtuplizer()
{
  delete metaGraph;
  metaGraph = nullptr;
  tensorflow::closeSession(session);
  session=nullptr;
}

void kerasCICADAModelNtuplizer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{ 
  modelOutput = 0.0;
  
  edm::Handle<std::vector<L1CaloRegion>> regions;
  iEvent.getByToken(emuRegionsToken, regions);

  tensorflow::Tensor modelInput(tensorflow::DT_FLOAT, {1,18*14});

  for (const L1CaloRegion& theRegion: *regions)
    {
      modelInput.tensor<float, 2>()(0, theRegion.gctPhi()*14 + (theRegion.gctEta()-4)) = theRegion.et();
    }

  std::vector<tensorflow::Tensor> tensorOutput;
  tensorflow::run(session, {{"serving_default_inputs:0", modelInput}}, {"StatefulPartitionedCall:0"}, &tensorOutput);

  modelOutput = tensorOutput[0].matrix<float>()(0, 0);

  triggerTree->Fill();
}

DEFINE_FWK_MODULE(kerasCICADAModelNtuplizer);

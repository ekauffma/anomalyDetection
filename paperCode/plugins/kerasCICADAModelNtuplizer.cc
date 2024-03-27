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
  static void fillDescriptions(edm::ConfigurationDescriptions &);

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
  float noiseSuppressionLevel = 0.0;

  edm::Service<TFileService> theFileService;  
  TTree* triggerTree;

  std::string inputLayerName;
};

kerasCICADAModelNtuplizer::kerasCICADAModelNtuplizer(const edm::ParameterSet& iConfig):
  emuRegionsToken(consumes<L1CaloRegionCollection>(iConfig.getParameter<edm::InputTag>("regionToken"))),
  branchName(iConfig.getParameter<std::string>("branchName")),
  treeName(iConfig.getParameter<std::string>("treeName"))
{
  usesResource("TFileService");

  inputLayerName = iConfig.exists("inputLayerName") ? iConfig.getParameter<std::string>("inputLayerName"): "serving_default_inputs_:0";
  std::string fullPathToModel(std::getenv("CMSSW_BASE"));
  fullPathToModel.append(iConfig.getParameter<std::string>("modelLocation"));
  // FileInPath doesn't like directories...
  // edm::FileInPath theFilePath = iConfig.getParameter<edm::FileInPath>("modelLocation");
  // std::string fullPathToModel = theFilePath.fullPath();

  if (iConfig.existsAs<int>("noiseSuppressionLevel"))
    noiseSuppressionLevel = (float) iConfig.getParameter<int>("noiseSuppressionLevel");
  else
    noiseSuppressionLevel = 0.0;
	 
  
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
      float towerEnergy = theRegion.et();
      float fillEnergy = 0.0;
      if (towerEnergy > noiseSuppressionLevel)
	fillEnergy = towerEnergy;
      modelInput.tensor<float, 2>()(0, theRegion.gctPhi()*14 + (theRegion.gctEta()-4)) = fillEnergy;
    }

  std::vector<tensorflow::Tensor> tensorOutput;
  tensorflow::run(session, {{inputLayerName.c_str(), modelInput}}, {"StatefulPartitionedCall:0"}, &tensorOutput);

  modelOutput = tensorOutput[0].matrix<float>()(0, 0);

  triggerTree->Fill();
}

void kerasCICADAModelNtuplizer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("regionToken", edm::InputTag("simCaloStage2Layer1Digis"));
  desc.add<std::string>("branchName");
  desc.add<std::string>("treeName");
  desc.add<std::string>("modelLocation");
  desc.addOptional<std::string>("inputLayerName");
  desc.addOptional<int>("noiseSuppressionLevel");
  descriptions.add("kerasCICADAModelNtuplizer", desc);
}

DEFINE_FWK_MODULE(kerasCICADAModelNtuplizer);

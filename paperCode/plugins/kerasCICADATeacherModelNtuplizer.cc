// Class for monitoring the performance of the CICADA teacher models
// to be attached to file trees for processing

#include <memory>

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
#include <cmath>

class kerasCICADATeacherModelNtuplizer : public edm::one::EDAnalyzer< edm::one::SharedResources >
{
public:
  explicit kerasCICADATeacherModelNtuplizer(const edm::ParameterSet&);
  ~kerasCICADATeacherModelNtuplizer() override;
  static void fillDescriptions(edm::ConfigurationDescriptions &);

private:
  void beginJob() override {};
  void analyze(const edm::Event&, const edm::EventSetup&) override;
  void endJob() override {};
  float averageSquareErrors( const std::vector<float>& );

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
};

kerasCICADATeacherModelNtuplizer::kerasCICADATeacherModelNtuplizer(const edm::ParameterSet& iConfig):
  emuRegionsToken(consumes<L1CaloRegionCollection>(iConfig.getParameter<edm::InputTag>("regionToken"))),
  branchName(iConfig.getParameter<std::string>("branchName")),
  treeName(iConfig.getParameter<std::string>("treeName"))
{
  usesResource("TFileService");
  
  std::string fullPathToModel(std::getenv("CMSSW_BASE"));
  fullPathToModel.append(iConfig.getParameter<std::string>("modelLocation"));

  if (iConfig.existsAs<int>("noiseSuppressionLevel"))
    noiseSuppressionLevel = (float) iConfig.getParameter<int>("noiseSuppressionLevel");
  else
    noiseSuppressionLevel = 0.0;

  triggerTree = theFileService->make<TTree>(treeName.c_str(), "keras teacher model output");
  triggerTree->Branch(branchName.c_str(), &modelOutput);

  metaGraph = tensorflow::loadMetaGraphDef(fullPathToModel);
  session = tensorflow::createSession(metaGraph, fullPathToModel, options);
}

kerasCICADATeacherModelNtuplizer::~kerasCICADATeacherModelNtuplizer()
{
  delete metaGraph;
  metaGraph = nullptr;
  tensorflow::closeSession(session);
  session=nullptr;
}

void kerasCICADATeacherModelNtuplizer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  modelOutput = 0.0;
  std::vector<float> squareModelErrors;

  edm::Handle<std::vector<L1CaloRegion>> regions;
  iEvent.getByToken(emuRegionsToken, regions);
  
  tensorflow::Tensor modelInput(tensorflow::DT_FLOAT, {1, 18*14});
  for (const L1CaloRegion& theRegion: *regions)
    {
      float towerEnergy = theRegion.et();
      float fillEnergy = 0.0;
      if (towerEnergy > noiseSuppressionLevel)
	fillEnergy = towerEnergy;
      modelInput.tensor<float, 2>()(0, theRegion.gctPhi()*14 + (theRegion.gctEta()-4)) = fillEnergy;
    }

  std::vector<tensorflow::Tensor> tensorOutput;
  tensorflow::run(session, {{"serving_default_teacher_inputs_:0", modelInput}}, {"StatefulPartitionedCall:0"}, &tensorOutput);

  tensorflow::Tensor resultTensor = tensorOutput.at(0);
  for (const L1CaloRegion& theRegion: *regions)
    {
      float modelPrediction = resultTensor.tensor<float, 4>()(0, theRegion.gctPhi(), theRegion.gctEta()-4, 0);
      float trueValue = modelInput.tensor<float, 2>()(0, theRegion.gctPhi()*14 + (theRegion.gctEta()-4));
      squareModelErrors.push_back(pow(trueValue-modelPrediction, 2));
    }
  modelOutput = sqrt(averageSquareErrors(squareModelErrors));
  
  triggerTree->Fill();
}

float kerasCICADATeacherModelNtuplizer::averageSquareErrors(const std::vector<float>& theVec)
{
  float average = 0.0;
  for (const float& val: theVec)
    average += val;
  average = average / (float)theVec.size();
  return average;
}

void kerasCICADATeacherModelNtuplizer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) 
{
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("regionToken", edm::InputTag("simCaloStage2Layer1Digis"));
  desc.add<std::string>("branchName");
  desc.add<std::string>("treeName");
  desc.add<std::string>("modelLocation");
  desc.addOptional<int>("noiseSuppressionLevel");
  descriptions.add("kerasCICADATeacherModelNtuplizer", desc);
}

DEFINE_FWK_MODULE(kerasCICADATeacherModelNtuplizer);

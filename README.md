# Main repository for Anomaly Detection work and submodules.
## Setup for paper studies (Jan 19th, 2024):
### Initial CMSSW Setup
```
#set-up the initial CMSSW repository
cmsrel CMSSW_14_0_0_pre2
cd CMSSW_14_0_0_pre2/src/
cmsenv && git cms-init

#Add the L1TCaloLayer 1 where the CICADA emulator proper is
git cms-addpkg L1Trigger/L1TCaloLayer1

#Get some of the modifications/configurations I have made for running multiple copies of the emulator
git cms-rebase-topic aloeliger:CICADA_Paper_Mods_14_0_0_pre2

#Get this repository
git clone --recursive https://github.com/aloeliger/anomalyDetection.git
#Now we need to get CICADA firmware models for the emulator and some of the things we use for that
cd anomalyDetection/
#need to get the xilinx ap_types repo, but need it to be called "hls" for CMSSW reasons
git clone https://github.com/Xilinx/HLS_arbitrary_Precision_Types hls

#Now, we first try compiling the CICADA firmware models
cd hls4mlEmulatorExtras/
make install #important to do this instead of just making it.
cd ../CICADA/
make #if this causes errors, stop, either try to fix them or reach out to me/someone
cd ../../
scram b -j 8 #make everything else,may complain about some scripts or non-cmssw files. Should work. mostly.
```
### Paper code
This repository is a mix of a large number of different sub-projects (and even repositories) I have created working on the CICADA project. I am trying to centralize all paper under the `paperCode` directory.
In particular, for making initial Ntuples, I am using `paperCode/python/makeCICADANtuplesFromRAW.py`.

This configuration is designed to run the last two models of both CICADA architectures (1.1.1, 1.1.2, 2.1.1, & 2.1.2 as of the writing of this), make enough input to make new models, and include L1Ntuple information. Running this many emulators at once is why we are working with some non-standard emulation code and configurations I have included.

This configuration is designed to run on RAW datatier files. I will be adding/modifying it in the future for MINI and MINI+RAW files. It is currently set-up for MC, I will be modifying it in the future to have a flag for data

The configuration should use most of the basic options for `analysis` described [here](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideAboutPythonConfigFile#VarParsing_Example)

In general, to run this configuration for a specific file, you can do:
```
cmsRun makeCICADANtuplesFromRAW.py inputFiles=/store/mc/campaign/sample/tier/file.root outputFile=file:./TestFile.root maxEvents=-1
```

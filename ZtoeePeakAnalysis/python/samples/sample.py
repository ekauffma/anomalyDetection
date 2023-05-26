#!/usr/bin/env python3

import ROOT

class sample:
    def __init__(self, listOfFiles:list[str], listOfChains:list[str]):
        self.listOfFiles = listOfFiles

        self.chainNames = []

        for chainName in listOfChains:
            finalChainName = chainName.split('/')[-1]
            setattr(self, finalChainName, ROOT.TChain(chainName))
            self.chainNames.append(finalChainName)
        
        for chainName in self.chainNames:
            for fileName in self.listOfFiles:
                getattr(self, chainName).Add(fileName)
        
        self.chain = getattr(self, self.chainNames[0])

        if len(self.chainNames) > 1:
            for chainName in self.chainNames[1:]:
                self.chain.AddFriend(getattr(self, chainName))
    
        self.weightingFunction = self.GetDefaultWeight

    def GetEntry(self, entryNum: int):
        self.chain.GetEntry(entryNum)

    def GetEntries(self) -> int:
        return self.chain.GetEntries()
    
    def GetDefaultWeight(self, *otherArgs)-> int:
        return 1.0

    def GetWeight(self, *otherArgs)-> int:
        return self.weightingFunction(self, *otherArgs)
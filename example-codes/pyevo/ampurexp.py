#AmpureXP 96 Well PCR Purification
#http://www.beckmangenomics.com/documents/products/ampurexp/AMPureXPProtocol_000387v001.pdf
import pyevo
pyevo.checkVersion(1)

evo = pyevo.EVO()
evo.logon()
s = pyevo.RobotScripter(evo,True)

#add in code to open script

reactionVolume = 10
ampureXPtoReactionVolumeRatio = 1.8
ampureXPReactionWells = [s.getFreeWell() for x in range(1,8)]
ampureXPLocationWell = pyevo.Well(9,0,1,1)

def AmpureXP(reactionWells):
    ampureXPAmount = ampureXPtoReactionVolumeRatio*reactionVolume
    for well in reactionWells:
        s.aspirate(1,ampureXPLocation,ampureXPAmount)
        s.dispense(1,well,ampureXPAmount)
    print "Pipette Mixing..."
    #pipette mix each well 10 times
    for well in reactionWells:
        s.pipetteMix(1,well,ampureXPAmount,10)

#run AmpureXP
#AmpureXP(ampureXPReactionWells)

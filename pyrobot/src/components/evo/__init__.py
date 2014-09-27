###############################################################################
##
##                    TECAN EVO WORKLIST GENERATOR
##
##                          tecanator V 0.3
##
##   Authors:                Sonya Hanson
##                          Jan-Hendrik Prinz
##                          John D. Chodera
##
###############################################################################


# March 28, 2014 Jan-Hendrik Prinz and Sonya Hanson play with robot.
# Set up triplicates of Src-Bosutinib binding assay in 5 different plate types.
# Updated with full plate types. March 31, 2014.
# Added classes for objects used in pipetting
# Apr 15th fixed first running version with classes

# TODO:
# Add documentation !!!!!!!!!!!!!!!!!!!!!!
# Add dispense schemes to compute estimates of accuracies
# Add detailed output for plate definition in some kind of XML format containing amounts and errors
# Add Advances WL commands to D300Worklist
# Think about use of Units, maybe switch to other units package
# Clean up parsing stuff in util.Parser
# Clean up WellSet, Well using util.Place





from Plate import Plate
from Mixture import Mixture
from Well import Well
from Well import Source
from WellSet import WellSet
from D300Worklist import D300Worklist
from util.Units import C
from util.Units import V 
from Task import Task
from Task import Scheduler
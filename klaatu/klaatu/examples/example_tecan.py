#!/usr/bin/env python

# ##############################################################################
# #
##                    TECAN EVO WORKLIST GENERATOR
##
##                          tecanerator V 0.3
##
##   Authors:               Sonya Hanson
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
# Add Advances WL commands to Worklist
# Think about use of Units, maybe switch to other units package
# Clean up parsing stuff in evo.Parser
# Clean up WellSet, Well using evo.Place

from klaatu.components.evo import Plate, Worklist, Source, Mixture, Scheduler, V

################################################################################
##  SOURCE PLATE DEFINITIONS
################################################################################

source_plate2 = Plate({'label': 'Source', 'racktype': '5x3 Vial Holder'})

source_plate = Plate({'label': 'Source', 'racktype': 'Troph Plate'})


################################################################################
##  TARGET PLATE DEFINITIONS
################################################################################

target_plates = [
    Plate({'label': 'Corning3651', 'racktype': 'Corning 3651'}),
    Plate({'label': 'corning 3651', 'racktype': '96 Well Microplate'}),
    Plate({'label': '96well-UVStar', 'racktype': '96 Well Microplate'}),
    Plate({'label': 'Corning3679', 'racktype': 'Corning 3679'}),
    Plate({'label': '384well', 'racktype': '384 Well Plate'}),
    Plate({'label': '384well2', 'racktype': '384 Well Plate'}),
    Plate({'label': '384well3', 'racktype': '384 Well Plate'})
]



################################################################################
##  SOURCE WELL DEFINITIONS
################################################################################

source_buffer_troph = Source({
    'description': 'Buffer',
    'label': 'Buffer',
    'plate': source_plate,
    'mixture': Mixture({
        'Buffer': '100%'
    }),
    'volume': '100ml',
    'well': 'A1'
}
)

source_protein_L = Source({
    'description': 'Protein Low C',
    'label': 'Protein_Low',
    'plate': source_plate,
    'mixture': Mixture({
        'Protein_L': '100%'
    }),
    'volume': '10ml',
    'well': 'A1'
}
)

source_protein_H = Source({
    'description': 'Protein High C',
    'label': 'Protein_High',
    'plate': source_plate,
    'mixture': Mixture({
        'Protein_H': '100%'
    }),
    'volume': '10ml',
    'well': 'B1'
}
)

source_buffer = Source({
    'description': 'Buffer Solution',
    'label': 'Buffer',
    'plate': source_plate,
    'mixture': Mixture({
        'Buffer': '100%'
    }),
    'volume': '10ml',
    'well': 'C1'
}
)

source_bosutinib_list = [
    Source({
        'description': 'Bosutinib #' + str(no) + " in concentration xyz",
        'label': 'Bosutinib' + str(no),
        'plate': source_plate,
        'mixture': Mixture({
            'Bosutinib#' + str(no): '100%'
        }),
        'volume': '10ml',
        'well': 'C1'
    }
    )
    for no in range(1, 13)
]

sources = [source_protein_L, source_protein_H, source_buffer] + source_bosutinib_list

################################################################################
##  TARGET WELL DEFINITION BY RULES
################################################################################

#well_rules = [
#    { 'cmd' : 'set', 'wells': 'A,C,E:1-12', 'mixture' : { 'Protein_H' : '75%'} },
#    { 'cmd' : 'set', 'wells': 'B,D,F:1-12', 'mixture' : { 'Protein_L' : '75%'} },
#    { 'cmd' : 'set', 'wells': 'G:1-12', 'mixture' : { 'Buffer' : '75%'} },
#    { 'cmd' : 'add', 'wells': 'A-G:1-12', 'mixture' : { 'Bosutinib#{col}' : '25%'} },
#    { 'target' : 'Corning3651', 'wells' : 'A-G:1-12', 'volume' : '75ul'},
#    { 'target' : '96well-UVStar', 'wells' : 'A-G:1-12', 'volume' : '75ul'},
#    { 'target' : 'Corning3679', 'wells' : 'A-G:1-12', 'volume' : '50ul'},
#    { 'target' : '384well(.*)', 'wells' : 'A-G:1-12', 'volume' : '20ul'}
#    { 'cmd' : 'add', 'wells': 'A-G:1-11', 'mixture' : { 'Compound #1' : '100 ** {%(col)} nM'} }
#]

# plate rules can contain 'wells' and 'target' to specify for which something is set 
# 'mixture' specifies the mixture as a dictionary of the liquid : concentration in Molar or %
# 'volume' species the desired target volume of the liquid

plate_rules = [
    {'wells': 'A,C,E:1-12', 'mixture': {'Protein_H': '100%'}},
    {'wells': 'B,D,F:1-12', 'mixture': {'Protein_L': '100%'}},
    {'wells': 'G:1-12', 'mixture': {'Buffer': '100%'}},
    {'target': 'Corning3651', 'wells': 'A-G:1-12', 'volume': '75ul'},
    {'target': '96well-UVStar', 'wells': 'A-G:1-12', 'volume': '75ul'},
    {'target': 'Corning3679', 'wells': 'A-G:1-12', 'volume': '50ul'},
    {'target': '384well(.*)', 'wells': 'A-G:1-12', 'volume': '20ul'}
]

for target in target_plates:
    target.apply_rule(plate_rules)

################################################################################
##  GENERATE SCHEDULER USING SOURCES, TARGETS AND RULES
################################################################################

sc = Scheduler(sources, target_plates)
sc.generate()

# apply a list of rules to specify the usage of the heads

# the first rule specifies that sources that match '' which is all, should be assigned to the head that has the target row
# the second rule overrides this for all the Bosutinib sources and specifies that these should be assigned always to the next free head among head 1-6
# so bosutinib#1 is head 1, ... bosutinib #6 is head 6, bosutinib #7 is head 1, ...

# usually things that are similar in rows should be dispensed using row, while col wise things should be used with free

task_rules = [
    {'source': '', 'head': '1-7', 'assignment': 'row'},
    {'source': 'Bosutinib(.*?)', 'head': '1-6', 'assignment': 'free'}
]

sc.apply_rule(task_rules)

# Build worklist generator
wl = D300Worklist()

# Write scheduled tasks to worklist
sc.write_to_worklist(wl)

worklist_filename = 'plate_types-worklist-protein_new-final.gwl'
outfile = open(worklist_filename, 'w')
outfile.write(wl.script)
outfile.close()

# Report

print
print "Dispense Actions"

for index in range(1, 9):
    print "head", index, " aspirates : ", sc.dispense_volumes[index], 'total : ', sum(sc.dispense_volumes[index])

print
print "Used liquids"

for (source_index, source) in enumerate(sources):
    if sc.volume_consumed[source.label] > 0.0:
        print "{:<20s}:       {:.3f} uL of {:.3f} uL ".format(source.label, sc.volume_consumed[source.label], V(source.volume).val('u'))

print "System Liquid (max) :        {:.3f} uL".format((wl.used_system_liquid()).val('u'))

print
print "Performed Actions"

print "Aspirations:           %(number)4d" % {'number': wl.aspirations}
print "Dispenses:             %(number)4d" % {'number': wl.dispenses}
print "Washs (max):           %(number)4d" % {'number': wl.washs}
'''
Created on 27.07.2014

@author: Jan-Hendrik Prinz
'''

from lxml import etree
from lxml import objectify

from util.xmlutil.XMLWalk import XMLWalker, XPathAnalyzer
from util.xmlutil.XMLBind import XMLBind 
from util.xmlutil.XMLFactory import XMLFactory

import components.momentum.converter as cv

import copy

# Read a Tecan Infinite Result XML file

root = objectify.fromstring(etree.tostring(objectify.parse('infinite_temp.xmlutil')))

o = XMLBind(root, namespaces = {'ns' : 'tecan.at.schema.documents'}, addns = True)

for key, value in o.inspect(unique = True, nodes= True).iteritems():
    print key, ":", value
    

o.bind('type', '//ReadingFilter/@type')

print o.type

o.bind('run', '//PlateRange')
o.bind('type', '//ReadingFilter/@type')

run = o.run

print run



add = run[0:1] + copy.deepcopy( run )
o.run = add

# Alternative form - a little longer
#o['type'] = 'manual'
o.type = 'man'

print o.type
print etree.tostring(o.xobj , pretty_print = True)

fac = XMLFactory()

template = etree.tostring(root.TecanMeasurement.MeasurementManualCycle.CyclePlate.PlateRange.MeasurementAbsorbance)
template = etree.tostring(root.xpath('//ns:MeasurementFluoInt', namespaces = {'ns' : 'tecan.at.schema.documents'})[0])

absorbance_measurement = fac.create_from_string(
    template, 
            {
                'diameter' : '//MeasurementReading/@beamDiameter',
                'wavelength' : '//ReadingFilter[2]/@wavelength'
              },
    namespaces = {'ns' : 'tecan.at.schema.documents'})


xobj2 = absorbance_measurement(diameter = 20, wavelength = 3800)
print xobj2
print etree.tostring(xobj2, pretty_print = True)

    
tst = root.xpath('//ns:MeasurementFluoInt[1]//ns:ReadingFilter[2]/@type', namespaces = {'ns' : 'tecan.at.schema.documents'})
print tst[0]

# bind_id will bind all matching elements and allow to to increasing number starting with the value set.
# o.id = 1 will set the first appearing @id to 1, the next to 2, etc...

# Select all @id, note we do not need to take care of the namespace, this is handled internally in a way that leaves the
# 
#o.bind_id('id', '//@id')

# Alternatively select only the ones previosly not zero
o.bind_id('id', "//*[@id != 0]/@id")

print o.id

# This actually calls the update
o.id = 1
# And show all ids
print o.id

# print etree.tostring(o.xobj , pretty_print = True)

o2 = XMLBind(objectify.fromstring(template), namespaces = {'ns' : 'tecan.at.schema.documents'} )

for key, value in o2.inspect(unique = True).iteritems():
    print key, ":", value

# Walker Test with namespace

wc = XMLWalker(root)
xp = "//ReadingFilter?type=@type"

result = wc.walk(XPathAnalyzer(xp, namespaces = {'ns' : 'tecan.at.schema.documents'} ))

print len(result)
print result

# Walker Test without namespace

root = objectify.fromstring(etree.tostring(objectify.parse('gen.xmlutil')))

wc = XMLWalker(root)
xp = "//Well?pos=@Pos/Scan?wave=@WL&val=text()"

result = wc.walk(XPathAnalyzer(xp))

print len(result)
print result[0]

#Try it with  mometum.mpr files and the converter

mom_mpr = ''

with open ('plAnalysis.mpr', "r") as myfile:
    mom_mpr = myfile.read()
    
xml = cv.momentum_to_xml(mom_mpr)

print xml

root = objectify.fromstring(xml)

o = XMLBind(root)

#for key, value in o.inspect(unique = False, nodes= True).iteritems():
#    print key, ":", value

wa = XMLWalker(root)

print root.xpath('//process/containers/item')
plates = wa.walk(XPathAnalyzer('//process/containers/item?name=@id'))

print plates

binder = XMLBind(root)

print root.xpath("//process/containers/item[@id = 'ActivePlate']")

binder.bind('plate', "//process/containers/item[@id = 'ActivePlate']/@id")

binder.plate = 'DeactivatedPlate'

#print cv.xml_to_momentum(binder.tostring())

process_steps = root.xpath("//process/comment[text() = 'Process steps']/following-sibling::*//if")
print [step.tag for step in process_steps]

process_steps = root.xpath("//process//set")
print [step.tag for step in process_steps]

root = objectify.fromstring(etree.tostring(objectify.parse('DMSO Concentration Test 2014-07-30 1940.DATA.xmlutil')))

print etree.tostring(root, pretty_print = True)

wk = XMLWalker(root)

dispenses = wk.walk(XPathAnalyzer('//Well?row=@R&col=@C/Fluid?index=@Index&total=@TotalVolume/Detail?time=@Time&cassette=@Cassette&head=@Head&volume=@Volume'))

#print dispenses

heads = wk.walk(XPathAnalyzer('//DispenseHead?type=@Type&cassette=@Cassette&head=@Head&fluid=@Fluid/LoadVolume?volume=text()'))
heads = wk.walk(XPathAnalyzer("//DispenseHead?head=@Head&fluid=@Fluid&total='LoadVolume/text()'&dispense='DispenseVolume/text()'"))

print etree.tostring(root.Fluids, pretty_print = True)

print heads
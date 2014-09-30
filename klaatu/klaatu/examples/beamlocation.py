"""
Created on 09.05.2014

@author: Sonya Hanson
@author: Jan-Hendrik Prinz
"""

# This script takes xmlutil data file output from the Tecan Infinite m1000 Pro plate reader 
# and makes quick and dirty images of the raw data.

# The same procedure can be used to make matrices suitable for analysis using
# matrix = dataframe.values

# Made by Sonya Hanson with significant help from JH Prinz.
# Wednesday, May 7, 2014

# Usage: python xml2png.py *.xmlutil

###################
# To Do
#
# Set fixed Y axis.
# Define Wells for Legend.
# Define x and y axes.
# Figure out @Name='Mode' thing.
#
###################

#from klaatu.components.distributor.googledrive import Distributor
from klaatu.util.xmlutil.XMLWalk import XMLWalker, XPathAnalyzer
from lxml import objectify, etree
import numpy as np
import sys

#db = Distributor()
#files = db.ls('infinite_result') 
#s = db.get(files[2]['id'])

#root = objectify.fromstring(s, parser=None)

#root = objectify.parse('filename.xml')

root = objectify.fromstring(etree.tostring(objectify.parse('E_PTT_BeamLocation_A12345678W_20140729_225738.xml')))


print etree.tostring(root, pretty_print = True)

# root.xpath('//Section/Data/Well/Multiple')
# root.xpath('//Section[@Name='Label1']/Data/Well/Multiple')
# root.xpath('//Section[@Name='Label1']/Data/Well/Multiple?pos=@MRW_Position')
# root.xpath('//Section[@Name='Label1']/Data/Well/Multiple/@MRW_Position')

wk = XMLWalker(root)
data = wk.walk(XPathAnalyzer("//Section[@Name='Label1']/Data/Well?well=@Pos/Multiple?pos=@MRW_Position&value='/text()'"))

print data

beams = {}

for d in data:
    p = d['pos'].split(';')
    if len(p) > 1:
        if d['well'] not in beams:
            beams[d['well']] = np.ones([15,15]) * (-0.1)
            
        beams[d['well']][int(p[0]), int(p[1])] = float(d['value'])

grayscale = " .:-=+*#%@"
gsl = len(grayscale)


for well in beams:
    welldata = beams[well]

    ma = np.amax(welldata)
    mi = np.amin(welldata)


    print
    print "Well", well
    print

    for y in range(15):
        for x in range(15):
            val = welldata[y,x]
            c = int(gsl * (val - mi) / (ma - mi + 0.000001))
            sys.stdout.write(grayscale[c])
        print ""

for b in beams:
    np.savetxt(b + ".csv", beams[b], delimiter=",")

exit()
    
import matplotlib as ml
ml.use('MacOSX') 
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(6, 3.2))

ax = fig.add_subplot(111)
ax.set_title('colorMap')
plt.imshow(beams['A1'])
ax.set_aspect('equal')

#cax = fig.add_axes([0.12, 0.1, 0.78, 0.8])
#cax.get_xaxis().set_visible(False)
#cax.get_yaxis().set_visible(False)
#cax.patch.set_alpha(0)
#cax.set_frame_on(False)
plt.colorbar(orientation='vertical')
plt.show()

exit()
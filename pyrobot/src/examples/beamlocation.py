'''
Created on 09.05.2014

@author: Sonya Hanson
@author: Jan-Hendrik Prinz
'''

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

from components.distributor.googledrive import Distributor
from util.xmlutil.XMLWalk import XMLWalker, XPathAnalyzer
from lxml import objectify, etree

import pandas as pd
import sys
import os

# Define extract function that extracts parameters

def extract(taglist):
    result = []
    for psr in taglist:
        param = parameters.xpath("*[@Name='" + psr + "']")[0]
        result.append( psr + '=' + param.attrib['Value'])
        
    return result
 
# Define get_wells_from_section function that extracts the data from each Section.
# It is written sort of strangely to ensure data is connected to the correct well.
    
def get_wells_from_section(path):
    reads = path.xpath("*/Well")
    wellIDs = [read.attrib['Pos'] for read in reads]

    data = [(float(s.text), r.attrib['Pos'])
         for r in reads
         for s in r]

    datalist = {
      well : value
      for (value, well) in data
    }
    
    welllist = [
                [
                 datalist[chr(64 + row) + str(col)]          
                 if chr(64 + row) + str(col) in datalist else None
                 for row in range(1,17)
                ]
                for col in range(1,24)
                ]
                
    return welllist

db = Distributor()
files = db.ls('infinite_result') 
s = db.get(files[2]['id'])

import numpy as np


root = objectify.fromstring(s, parser=None)

# print etree.tostring(root, pretty_print = True)

wk = XMLWalker(root)
data = wk.walk(XPathAnalyzer("//Section[@Name='Label1']/Data/Well?well=@Pos/Multiple?pos=@MRW_Position&value='/text()'"))

beams = {}

for d in data:
    p = d['pos'].split(';')
    if len(p) > 1:
        if d['well'] not in beams:
            beams[d['well']] = np.ones([15,15]) * 
            
        beams[d['well']][int(p[0]) - 1, int(p[1]) - 1] = float(d['value'])

grayscale = """$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^`'. """
grayscale = " .:-=+*#%@"
gsl = len(grayscale)

print gsl

ma = np.amax(beams['A1'])
mi = np.amin(beams['A1'])

for well in beams:
    welldata = beams[well]

    print
    print "Well", well
    print

    for y in range(15):
        for x in range(15):
            val = welldata[y,x]
            c = int(gsl * (val - mi) / (ma - mi + 0.000001))
            sys.stdout.write(grayscale[c])
        print ""

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

Sections = root.xpath("/*/Section")
much = len(Sections)
print "****The xmlutil file " + file + " has %s data sections:****" % much
for sect in Sections:
    print sect.attrib['Name'] 

data = []


for i, sect in enumerate(Sections):

    # Extract Parameters for this section.
   
    path = "/*/Section[@Name='" + sect.attrib['Name'] + "']/Parameters"
    parameters = root.xpath(path)[0]

    # Parameters are extracted slightly differently depending on Absorbance or Fluorescence read.
    
    title = ''
            
    if  parameters[0].attrib['Value'] == "12":   
        result = extract(["Mode", "Wavelength", "Part of Plate"])
        title = '%s, %s, %s' % tuple(result)

    else:
        result = extract(["Wavelength Start", "Wavelength End", "Mode"])
#            title = '%s, %s, %s, \n %s, %s' % tuple(result)

    print "****The %sth section has the parameters:****" %i  
    print title
    
    # Extract Reads for this section.
    Sections = root.xpath("/*/Section")
    welllist = get_wells_from_section(sect)
    
    data.append(
        {
                'filename' : file_name,
                'title' : title,
                'dataframe' : pd.DataFrame(welllist) 
        }
    )

# Make plot, complete with subfigure for each section. 
fig, axes = plt.subplots(nrows=1,ncols=len(Sections), figsize=(20,4.5))

for i, sect in enumerate(data):
    sect['title'] = 'Hello'
    sect['dataframe'].plot(title = sect['title'], ax = axes[i])

fig.tight_layout()
fig.subplots_adjust(top=0.8)
fig.suptitle("%s" % file_name, fontsize=18)

plt.savefig('%s.png' % file_name)
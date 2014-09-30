'''
Created on 27.09.2014

@author: jan-hendrikprinz
'''
from util.xmlutil.XMLWalk import XMLWalker, XPathAnalyzer
from lxml import etree, objectify


class PlateRead(object):
    '''
    classdocs
    '''


    def __init__(self, part):
        '''
        Constructs a Parser object for a specific read type in an infinite result .xml
        '''

        self.xml = objectify.fromstring(etree.tostring(part))

        self.wc = XMLWalker(self.xml)
        self._wells = {}
        
    def read(self):
        return 
    
    @property
    def wells(self):    
        return self._wells
    
    @property
    def pandas(self):
        return

class AbsorbanceMultiRead(PlateRead):

    @staticmethod
    def well1_fnc(val):
        e = val.split(';')
        return e
    
    def __init__(self, xml):
        super(AbsorbanceMultiRead, self).__init__(xml)
        
        
        self.well1_fnc

        xp = "//Section/Data?run:int=@Cycle/Well?well=@Pos/Multiple?location:well1=@MRW_Position&value=text()"
        
        self.alz = XPathAnalyzer(xp)                            
        self.alz.add_custom_type('well1', self.well1_fnc)

        self.result = self.wc.walk(self.alz)
                

    def read(self):
        return
    

class Infinite(object):
    '''
    classdocs
    '''


    def __init__(self, xml):
        '''
        Constructs a Parser object for Infinite Result .xml
        '''
        
        self.xml = objectify.fromstring(etree.tostring(xml))
        
        self.barcode = self.xml.xpath('/MeasurementResultData/Plate/BC/text()')
        self.sections = self.xml.xpath('/MeasurementResultData/Section')
        
        self.wc = XMLWalker(self.xml)

        xp = "//Section/Data?run:int=@Cycle" + "/Well?well=@Pos/Single?value:int=text()"
        xp = "//Section/Data?run:int=@Cycle/Well?well=@Pos/Multiple?location:well1=@MRW_Position&value=text()"
        
        pr = AbsorbanceMultiRead(self.sections[0])
                        
        print pr.result
            
file1 = 'E_PTT_BeamLocation_A12345678W_20140729_225738.xml'
file2 = 'result.xml'

root1 = objectify.parse(file1)
root2 = objectify.parse(file2)
    
inf = Infinite(root1)
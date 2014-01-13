
import simtk.unit as units

class Labware(object):
    pass

class SBSLabware(Labware):
    def __init__(self, name, type
                 manufacturer=None, 
                 catalog_number=None,
                 xwells=None,
                 ywells=None,
                 well_capacity=None,
                 color=None,
                 well_shape=None,
                 description=None,
                 url=None):
        self.name = name
        self.catalog_number = catalog_number
        self.xwells = xwells
        self.ywells = ywells
        self.well_capacity = well_capacity
        self.color = color
        self.well_shape = well_shape
        self.description = description
        self.url = url
    
    @property
    def wells(self):
        if self.xwells and self.ywells:
            return self.xwells * self.ywells
        else:
            return None


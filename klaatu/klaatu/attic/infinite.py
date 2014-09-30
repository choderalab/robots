"""
Created on 08.05.2014

@author: jan-hendrikprinz
"""

'''
Created on 07.05.2014

@author: jan-hendrikprinz
'''

# ###############################################################################
##  PLATE TYPE DEFINITIONS
################################################################################

from lxml import etree


class Script():
    @staticmethod
    def _get_subset(root, path, key='key', value='value'):
        return {
            element.attrib[key]: element.attrib[value]
            for element in root.xpath(path + "/*")
        }

    def __init__(self, *initial_data, **kwargs):

        # Defaults

        self.size = 96
        #        self.volume = '50ul'
        self.volume = '50'  # in ul
        self.vendor = 'unknown'
        self.model = 'unknown'
        self.bottom = False
        self.reference = {'momentum': '', 'evo': '', 'infinite': ''}

        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

        # this should be put into a database or XML File at some point

    @staticmethod
    def load(name):
        root = etree.parse('containers.xmlutil')

        profile = root.xpath("/document/profile")[0]
        process = profile.xpath("process")[0]

        profile_id = profile.attrib['id']

        parameters = {
            'params': Container._get_subset(profile, 'parameters')
        }
        references = {
            'refs': Container._get_subset(profile, 'references', 'device', 'id')
        }
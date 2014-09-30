"""
Created on 27.07.2014

@author: Jan-Hendrik Prinz
"""

from lxml import objectify

import copy

from klaatu.util.xmlutil.XMLBind import XMLBind
from klaatu.util.xmlutil.XMLInspect import XMLInspector
from lxml import etree


class XMLFactory(object):
    def __init__(self):
        self.binder = None
        pass

    def as_dict(self):
        return {key: self.binder[key] for key in self.binder._bindings.keys()}

    def __call__(self, **kwargs):
        for key, value in kwargs.iteritems():
            if key in self.binder._bindings.keys():
                # binding exists to set the value
                if type(value) is list:
                    self.binder[key] = value
                else:
                    self.binder[key] = str(value)
                # else:
                #                print self.binder._bindings.keys()
                #                print key, 'does not exist'

        # need a deep copy otherwise after each new generation all other objects would change as well!!!!
        return copy.deepcopy(self.binder.xobj)

    def reset(self):
        self(**self.default)

    def __str__(self, **kwargs):
        return self.str(**kwargs)

    def xml(self, **kwargs):
        return self(**kwargs)

    def str(self, **kwargs):
        return etree.tostring(self(**kwargs), pretty_print=True)

    @staticmethod
    def from_xml(xml, bindings=None, namespaces={'ns': ''}, addns=True):
        self = XMLFactory.from_string(etree.tostring(xml), bindings, namespaces, addns)
        return self

    @staticmethod
    def from_string(s, bindings=None, namespaces={'ns': ''}, addns=True):
        xml = objectify.fromstring(s)
        self = XMLFactory()
        self.binder = XMLBind(xml, namespaces, addns)

        if bindings is None:
            xins = XMLInspector(simplify=False, children=True)
            bindings = xins.bindings(xml)

        for name, b in bindings.iteritems():
            self.binder.bind(name, b)

        self.default = self.as_dict()

        return self

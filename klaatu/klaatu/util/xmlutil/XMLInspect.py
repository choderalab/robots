"""
Created on 27.09.2014

@author: Jan-Hendrik Prinz
"""
from klaatu.util.xmlutil.NSXPathUtil import NSXPathUtil
import re


class XMLInspector(NSXPathUtil):
    """
    Inspect the objectify object and list all attributes and notes with their xpath and type
       
    Parameters
    ----------
    unique : bool, optional
        If set to `True` all nodes and attributes are treated as unique and so will their xpath contain additional information to make the xpath
        unique to this specific node or attribute. Default is `False`.
    simplify : bool, optional
        If set to `True` the returned xpaths are simplified using `//` and skipping unnecessary xpath nodes along the path. Default is `True`.
    nodes : bool optional 
        If set to `True` nodes will be includes in the output. Default is `False`.
    attributes : bool, optional
        If set to `True` attributes will be included in the output. Default is `True`.
    
    """


    def __init__(self, unique=True, simplify=True, nodes=False, attributes=True, texts=True, children=False, enter_lists=False, namespaces={'ns': ''}, addns=True):

        self.unique = unique
        self.simplify = simplify
        self.nodes = nodes
        self.attributes = attributes
        self.texts = texts
        self.children = children
        self.enter_lists = enter_lists

        self.namespace = namespaces.values()[0]
        self.ns = namespaces.keys()[0]

        self.addns = addns

    @staticmethod
    def _tounderscore(name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @staticmethod
    def _isfloat(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def _isint(value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def _has_child_list(xml):
        nodes = xml.getchildren()
        if len(nodes) < 2:
            return False
        else:
            tag = nodes[0].tag
            for n in nodes:
                if tag != n.tag:
                    return False
            return True


    def xpaths(self, xml):
        """Returns only the xpaths to all xml nodes and attributes specified. Convinience function.
                
        See also
        --------        
        inspect
        
        """

        ins = self.inspect(self.unique, self.simplify, self.nodes, self.attributes)

        return ins.keys()


    def _get_nodes(self, node, result, path_src):
        if self.nodes:
            full = path_src
            if full not in result:
                result[full] = {'class': 'attribute', 'var': self._tounderscore(node.tag), 'type': 'object'}


    def _get_children(self, node, result, path_src):
        if self.children:
            if self._has_child_list(node):
                full = path_src
                if full not in result:
                    result[full] = {'class': 'children', 'var': self._tounderscore(node.tag), 'type': 'list'}


    def _get_texts(self, node, result, path_src):
        if self.texts:
            if node.text is not None:
                full = path_src + '/text()'
                if full not in result:
                    result[full] = {'class': 'text', 'var': self._tounderscore(node.tag), 'type': 'str'}


    def _get_attributes(self, node, result, path_src):
        if self.attributes:
            for att in node.attrib.keys():
                full = path_src + '/@' + att
                ty = 'str'
                val = node.attrib[att]
                vall = val.lower()
                valc = val
                if self._isfloat(val):
                    ty = 'float'
                    valc = float(val)
                if self._isint(val):
                    ty = 'int'
                    valc = int(val)
                if vall == "true" or vall == 'false':
                    ty = 'bool'
                    valc = bool(val[0].upper() + val[1:].lower())
                if full not in result:
                    result[full] = {'class': 'attribute', 'var': self._tounderscore(att), 'type': ty, 'values': [valc]}
                else:
                    result[full]['values'].append(valc)


    def _get_unique_path(self, node, path):
        if self.unique:
            path = []  # print node, node.tag
            # print 'Children', len(node.getchildren())
            ancestors = [anc for anc in node.iterancestors()]
            ancestors = [node] + ancestors
            for anc in ancestors:
                t = anc.tag
                if len(anc) > 1:
                    mat = [i for i in range(len(anc)) if anc[i] is anc][0]
                    t += '[' + str(mat + 1) + ']'
                path.append(t)

        else:
            path = [anc.tag for anc in node.iterancestors()]
            path = [node.tag] + path
        return path


    def _get_namespace_path(self, path):
        if self.namespace is not '':
            # the namespace stuff is a little cumbersome
            # this takes care of it
            if self.addns:
                path = [psr.split('}')[1] for psr in path]
            else:
                path = [self.ns + ':' + psr.split('}')[1] for psr in path]
        return path


    def _get_path(self, path):
        path_src = ''
        if self.simplify:
            path = [psr for psr in reversed(path)]
            path_src = '/'
            double = False
            for nn, psr in enumerate(path):
                if path[nn] not in path[:nn] and path[nn][-1] != ']' and nn < len(path) - 1:
                    double = True
                else:
                    if double:
                        path_src += '/'
                    double = False
                    path_src += path[nn]
                    if nn < len(path) - 1:
                        path_src += '/'

        else:
            path = [psr for psr in reversed(path)]
            path_src = '/'.join(path[0:])
            path_src = '/' + path_src
        return path_src

    def node(self, node):
        path_list = []

        path_list = self._get_unique_path(node, path_list)
        path_list = self._get_namespace_path(path_list)

        path = self._get_path(path_list)

        result = {}

        self._get_nodes(node, result, path)
        self._get_children(node, result, path)
        self._get_texts(node, result, path)
        self._get_attributes(node, result, path)

        return result

    def __call__(self, xml):
        self._full = self.node(xml)
        self._recurse(xml)

        return self._full

    def bindings(self, xml):
        return {details['var']: path for path, details in self(xml).iteritems()}

    def _recurse(self, xml):
        if self.enter_lists or not XMLInspector._has_child_list(xml):
            for node in xml.iterchildren():
                self._full.update(self.node(node))

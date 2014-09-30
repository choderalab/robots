"""
Created on 09.05.2014

@author: jan-hendrikprinz
"""

from lxml import etree
import string
import re


class XDict(dict):
    def _traverse(self, d, index, strip=False):
        out = d

        sp = index.split('/')

        path = sp[0]
        rest = "/".join(sp[1:])

        if '*' in path:
            if type(out) is dict:
                ret = {}
                for psr in out:
                    if re.search(string.replace(path, '*', '[\\S]+'), psr) is not None:
                        if not strip:
                            ret[psr] = self._traverse(out[psr], rest, strip)
                        else:
                            st = string.split(psr, ":")[-1]
                            ret[st] = self._traverse(out[psr], rest, strip)
            elif type(out) is list:
                if path.isdigit():
                    out = out[int(path)]
        elif path != '':
            if type(out) is dict:
                ret = self._traverse(out[path], rest, strip)
            elif type(out) is list:
                if path.isdigit():
                    ret = out[int(path)]
        else:
            ret = d
        return ret

    def get(self, index, strip=False):
        out = self._traverse(dict(self), index, strip)

        if type(out) is dict:
            return XDict(out)
        else:
            return out

    def __getitem__(self, index):
        out = self._traverse(dict(self), index)

        if type(out) is dict:
            return XDict(out)
        else:
            return out

    def __setitem__(self, index, value):
        out = dict(self)
        way = index.split('/')
        last = way[-1]
        way.pop()
        for path in way:
            if type(out) is dict:
                out = out[path]
            elif type(out) is list:
                if path.isdigit():
                    out = out[int(path)]
                else:
                    out = [i for i in out if i['id'] == path][0]

        if type(out) is dict:
            out[last] = value
        elif type(out) is list:
            if last.isdigit():
                out[int(last)] = value
            else:
                pos = [no for no, i in enumerate(out) if i['id'] == last][0]
                out[pos] = value


import collections


class XMLDict(collections.MutableMapping):
    """XMLDict is an ordered dict that allows to represent an XML tree and access elements similar to XML"""

    def __init__(self, *args, **kwargs):
        self.tag = ''
        self.store = dict(*args, **kwargs).iteritems()

    def update(self, d):
        self.store = d.iteritems()

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def _traverse(self, d, index, strip=False):
        out = d

        sp = index.split('/')

        path = sp[0]
        rest = "/".join(sp[1:])

        if '*' in path:
            if type(out) is dict:
                ret = {}
                for psr in out:
                    if re.search(string.replace(path, '*', '[\\S]+'), psr) is not None:
                        if not strip:
                            ret[psr] = self._traverse(out[psr], rest, strip)
                        else:
                            st = string.split(psr, ":")[-1]
                            ret[st] = self._traverse(out[psr], rest, strip)
            elif type(out) is list:
                if path.isdigit():
                    out = out[int(path)]
        elif path != '':
            if type(out) is dict:
                ret = self._traverse(out[path], rest, strip)
            elif type(out) is list:
                if path.isdigit():
                    ret = out[int(path)]
        else:
            ret = d
        return ret

    def get(self, index, strip=False):
        out = self._traverse(dict(self), index, strip)

        if type(out) is dict:
            return XDict(out)
        else:
            return out

    def __getitem__(self, index):
        out = self._traverse(dict(self), index)

        if type(out) is dict:
            return XDict(out)
        else:
            return out

    def __setitem__(self, index, value):
        out = dict(self)
        way = index.split('/')
        last = way[-1]
        way.pop()
        for path in way:
            if type(out) is dict:
                out = out[path]
            elif type(out) is list:
                if path.isdigit():
                    out = out[int(path)]
                else:
                    out = [i for i in out if i['id'] == path][0]

        if type(out) is dict:
            out[last] = value
        elif type(out) is list:
            if last.isdigit():
                out[int(last)] = value
            else:
                pos = [no for no, i in enumerate(out) if i['id'] == last][0]
                out[pos] = value


class XMLPyWrap(object):
    """
    Allows to define a conversion pattern between a python dict and an XML file
    """

    ATTRIBUTELIST = {
        'analysis': {'Well': '@Pos', 'Section': '@Name', 'Scan': '@WL'},
        'script': {'ReadingFilter': '@type', 'MeasurementFluoInt': 'Well/MeasurementReading/ReadingLabel@name'},
        'momentum': {'param': '@key', 'item': '@id'},
        'container': {'param': '@key', 'ref': 'device'}
    }

    def __init__(self, attribute):
        """
        Constructor
        """
        self.strip_first_line = True
        self.attribute = self.ATTRIBUTELIST[attribute]

    def xml_as_py(self, s):
        s = s.strip()

        root = etree.XML(s)
        return XDict(self._xml_to_obj(root))

    def py_as_xml(self, o):
        return self._obj_to_xml(o)

    def _obj_to_xml(self, obj):
        obj = dict(obj)
        s = '<' + obj['tag']
        for a in obj:
            if a != 'tag' and a != 'text':
                if type(obj[a]) is str:
                    s += " " + a + '="' + XMLPyWrap._xml_escape(obj[a]) + '"'

        s += '>'

        if 'text' in obj:
            s += obj['text']
        else:
            for a in obj['__order__']:
                if type(obj[a]) is dict:
                    s += self._obj_to_xml(obj[a])

        s += '</' + obj['tag'] + '>'
        return s

    @staticmethod
    def _xml_escape(s):
        s = string.replace(s, '<', '&lt;')
        s = string.replace(s, '>', '&gt;')
        s = string.replace(s, '&', '&amp;')
        s = string.replace(s, '"', '&quot;')
        return s

    @staticmethod
    def _xml_strip_namespace(s):
        i = s.find('}')
        if i >= 0:
            s = s[i + 1:]

        return s

    def _xml_to_obj(self, root):
        obj = {}
        rtag = XMLPyWrap._xml_strip_namespace(root.tag)
        obj['tag'] = rtag

        for t in root.attrib:
            obj[t] = root.attrib[t]

        children = root.xpath("*")

        order = []
        count = 1

        if len(children) > 0:
            for c in children:
                tag = XMLPyWrap._xml_strip_namespace(c.tag)

                add = self._xml_to_obj(c)
                if tag not in obj:
                    if tag in self.attribute:
                        pa = self.attribute[tag].split("@")
                        hpath = "@".join(pa[:-1])
                        htag = pa[-1]

                        if hpath != '':
                            hook = c.xpath(hpath)[0]
                        else:
                            hook = c

                        if htag in hook.attrib:
                            tag = tag + ":" + hook.attrib[htag]

                    obj[tag] = add
                    order.append(tag)
                else:
                    tag = tag + ':' + str(count)

                    count += 1

                    obj[tag] = add
                    order.append(tag)
        else:
            if root.text is not None:
                obj['text'] = root.text

        obj['__order__'] = order

        if rtag in self.attribute and False:
            pa = self.attribute[rtag].split("@")
            hpath = "@".join(pa[:-1])
            htag = pa[-1]

            if hpath != '':

                hook = root.xpath(hpath)[0]
            else:
                hook = root

            if htag in hook.attrib:
                obj = {hook.attrib[htag]: obj}

        return obj

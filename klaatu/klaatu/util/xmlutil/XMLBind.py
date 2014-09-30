"""
Created on 25.07.2014

@author: jan-hendrikprinz
"""

from lxml import etree, objectify
from klaatu.util.xmlutil.NSXPathUtil import NSXPathUtil


class XMLBind(NSXPathUtil):
    """Class to create bindings between instance properties and associated objectified xmlutil nodes/attributes.
    
    Attributes
    ----------
    xobj : lxml.objectify
        The associated lxml.objectify object that contains the XML as a python tree object
    
    Methods
    ----------
    bind
    inspect
    bind_id
    tostring

    Notes
    -----    
    The function creates a property `name` in the XMLBind instance that is persistantly linked to an XML part that is located
    in the instances lxml.objectify `self.xobj` property at the xpath given by `xpath`. A change in the instance property then
    result a change in the objectify object. Since this is given when the instance is created changes will also be present outside of
    the XMLBind instance itself. To avoid this you can use copy.deepcopy on the xobj before creating the class instance. 
    
    Examples
    --------
    
    Imports
    
    >>> from lxml import etree, objectify 
    >>> xmlutil = '<node value="20" />'
    
    Create objectify object to bind to
    >>> xobj = objectify.fromstring(xmlutil)
    
    Create binding object
    >>> xb = XMLBind(xobj)
    
    Create binding property `val` and bind it to the value attribue of node `node`
    >>> xb.bind('val', '/node/@value')
    >>> print xb.val
    20

    Use the property to access the `value` attribute
    >>> xb.val = '30'
    
    Return the xmlutil as formatted string
    >>> print etree.tostring(obj, pretty_print = True)
    <node value="30"></node>
    """


    def __init__(self, xobj, namespaces=None, addns=True):
        if not namespaces: namespaces = {'ns': ''}
        self.xobj = xobj
        self._bindings = {}
        self.namespace = namespaces.values()[0]
        self.ns = namespaces.keys()[0]

        self.addns = addns
        return

    def __getitem__(self, name):
        return self._bindings[name]['get']()

    def __setitem__(self, name, val):
        return self._bindings[name]['set'](val)

    def __getattribute__(self, name):
        if '_bindings' in object.__getattribute__(self, '__dict__'):
            bindings = object.__getattribute__(self, '_bindings')

            if name in bindings:
                if 'get' in bindings[name]:
                    return bindings[name]['get']()
                else:
                    return object.__getattribute__(self, name)
            else:
                return object.__getattribute__(self, name)
        else:
            return object.__getattribute__(self, name)


    def __setattr__(self, name, val):
        if '_bindings' in object.__getattribute__(self, '__dict__'):
            bindings = object.__getattribute__(self, '_bindings')
            if name in bindings:
                if 'set' in bindings[name]:
                    return bindings[name]['set'](val)
                else:
                    return object.__setattr__(self, name, val)
            else:
                return object.__setattr__(self, name, val)
        else:
            return object.__setattr__(self, name, val)

    def tostring(self, pretty_print=True):
        """Return the enclosed `self.xobj` as XML

        Optional Parameters
        -------------------
        pretty_print : bool
            If `True` the output has indention and line-breaks. See etree.tostring for further details.

        See also
        --------
        etree.tostring


        """
        return etree.tostring(self.xobj, pretty_print=pretty_print)


    def bind(self, name, xpath):
        """Create a binding between object property and a xmlutil node/attribute
        
        Parameters
        ----------
        name : string
            Name `name` of the class property to be created. Should be chosen according to python variable style - lower case and underscore separated.
        xpath : string of XPath type
            XPath `xpath` that specifies the location of the XML part to be bound to the class property

        Notes
        -----
        
        The function creates a property `name` in the XMLBind instance that is persistantly linked to an XML part that is located
        in the instances lxml.objectify `self.xobj` property at the xpath given by `xpath`. A change in the instance property then
        result a change in the objectify object. Since this is given when the instance is created changes will also be present outside of
        the XMLBind instance itself. To avoid this you can use copy.deepcopy on the xobj before creating the class instance. 
        
        Examples
        --------
        
        Imports
        
        >>> from lxml import etree, objectify 
        >>> xmlutil = '<node value="20" />'
        
        Create objectify object to bind to
        >>> xobj = objectify.fromstring(xmlutil)
        
        Create binding object
        >>> xb = XMLBind(xobj)
        
        Create binding property `val` and bind it to the value attribue of node `node`
        >>> xb.bind('val', '/node/@value')
        >>> print xb.val
        20

        Use the property to access the `value` attribute
        >>> xb.val = '30'
        
        Return the xmlutil as formatted string
        >>> print etree.tostring(obj, pretty_print = True)
        <node value="30"></node>
        """

        parts = self._xpath(self._wrapxpath(xpath))
        if len(parts) > 0:
            part = parts[0]
            if type(part) is objectify.ObjectifiedElement:
                self.bind_children(name, xpath)
            else:
                if part.is_attribute:
                    self.bind_attribute(name, xpath)
                elif part.is_text:
                    self.bind_text(name, xpath)
        else:
            # Throw an error here
            print xpath
            print 'XPath does not contain any elements to bind to'


    def bind_id(self, name, xpath):
        xpath = self._wrapxpath(xpath)

        def getter():
            parts = self._xpath(xpath)
            return [part.getparent().get(part.attrname) for part in parts]

        def setter(start):
            parts = self._xpath(xpath)
            for idx, part in enumerate(parts):
                part.getparent().set(part.attrname, str(idx + start))

            return

        setattr(self, name, setter)

        self._bindings[name] = {'get': getter, 'set': setter}


    def bind_attribute(self, name, xpath):

        xpath = self._wrapxpath(xpath)

        def getter():
            part = self._xpath(xpath)[0]
            parent = part.getparent()
            return parent.get(part.attrname)

        def setter(val):
            part = self._xpath(xpath)[0]
            parent = part.getparent()
            parent.set(part.attrname, val)
            return

        self._bindings[name] = {'get': getter, 'set': setter}

    def bind_text(self, name, xpath):
        xpath = self._wrapxpath(xpath)

        def getter():
            part = self._xpath(xpath)[0]
            parent = part.getparent()
            return parent.text

        def setter(val):
            part = self._xpath(xpath)[0]
            parent = part.getparent()
            parent._setText(val)
            return

        self._bindings[name] = {'get': getter, 'set': setter}

    def bind_children(self, name, xpath):
        xpath = self._wrapxpath(xpath)

        def getter():
            part = self._xpath(xpath)[0]
            return [c for c in part.iterchildren()]

        def setter(val):
            part = self._xpath(xpath)[0]
            for e in part.getchildren():
                part.remove(e)

            for elem in val:
                part.append(elem)
            return

        self._bindings[name] = {'get': getter, 'set': setter}

    def unbind(self, name):
        """Remove a binding

        Parameters
        ----------
        name : string
            key of the binding to be removed
        """
        del self._bindings[name]

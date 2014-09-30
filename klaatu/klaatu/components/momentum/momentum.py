"""
Created on 27.04.2014

@author: Jan-Hendrik Prinz
"""

import converter as cv
import components.momentum.momentum_templates as sc


class SimpleGetItem:
    """Mixin that allows easier access in nested mixed python dicts/lists. It allows to pick by either a key in dict, the ordinal
    number in an array or and the list item that has an id member with a given value.

    Notes
    -----

    The idea was to mimic XPath for nested python objects.

    ```
    data = [
        { 'id' : 'obj1', 'value' : 'cat'},
        { 'id' : 'obj2', 'value' : 'dog'}
    ]
    ```

    Now we can write `data['obj1']` or `data['obj1/value']`

    """

    def __getitem__(self, index):
        out = self.data
        for path in index.split('/'):
            if type(out) is dict:
                out = out[path]
            elif type(out) is list:
                if path.isdigit():
                    out = out[int(path)]
                else:
                    out = [i for i in out if i['id'] == path][0]
        return out

    def __setitem__(self, index, value):
        out = self.data
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


class Momentum(SimpleGetItem, sc.MomentumFactory):
    """A parser for ThermoFisher Momentum scripts

    Notes
    -----

    Should be constructed using factory functions `from...` or `read...`
    """

    def __init__(self):
        self.tokenlist = []
        self.name = ''
        self.data = {}

    @staticmethod
    def fromMomentum(s):
        """Constructs a Momentum instance from a string in form of a Momentum script

        Parameters
        ----------

        s : string
            string in Momentum script
        """
        obj = Momentum()
        obj.momentum = s
        obj.xml = cv.momentum_to_xml(obj.momentum)
        obj.data = cv.xml_to_python(obj.xml)
        obj.momentum = cv.python_to_momentum(obj.data)
        return obj

    @staticmethod
    def fromXML(s):
        """Constructs a Momentum instance from a string in form of XML

        Parameters
        ----------

        s : string
            string in XML

        Notes
        -----

        This is the proprietary XML scheme used by this package. There is no direct implementation or usage from ThermoFisher
        """

        obj = Momentum()
        obj.xml = s
        obj.data = cv.xml_to_python(obj.xml)
        obj.momentum = cv.python_to_momentum(obj.data)
        obj.xml = cv.momentum_to_xml(obj.momentum)
        return obj

    @staticmethod
    def fromPython(d):
        """Constructs a Momentum instance from a nested python dict

        Parameters
        ----------

        d : mixed
            nested python dict containing the structure of the Momentum script
        """
        obj = Momentum()
        obj.data = d
        obj.momentum = cv.python_to_momentum(obj.data)
        obj.xml = cv.momentum_to_xml(obj.momentum)
        obj.data = cv.xml_to_python(obj.xml)
        return obj

    def asMomentum(self):
        """Returns a string representation of the Momentum Script that can be imported in Momentum

        Returns
        -------
        s : string
            Returned Momentum string
        """
        return cv.python_to_momentum(self.data)

    def asPython(self):
        """Returns a nested python dict representation of the Momentum Script that can easily be edited

        Returns
        -------
        d : nested python dict
            Returned Momentum representation
        """
        return self.data

    def asXML(self):
        """Returns a XML representation of the Momentum Script that can be further processed using lxml, etc.

        Returns
        -------
        d : string
            Returned XML representation of the Momentum script
        """
        return cv.momentum_to_xml(self.asMomentum())

    @staticmethod
    def readMomentum(filename):
        """Construct a Momentum instance from a file exported from Momentum

        Returns
        -------

        x : Momentum
            newly created instance
        """
        with open(filename, "r") as myfile:
            return Momentum.fromMomentum(myfile.read())

    @staticmethod
    def readXML(filename):
        """Construct a Momentum instance from an XML file

        Returns
        -------

        x : Momentum
            newly created instance
        """
        with open(filename, "r") as myfile:
            return Momentum.fromXML(myfile.read())

    def toMomentumFile(self, filename):
        """Write the current Momentum script to a file to be imported into Momentum

        Parameters
        ----------

        filename : string
            filename to be written to
        """
        outfile = open(filename, 'w')
        outfile.write(self.asMomentum())
        outfile.close()

    def toXMLFile(self, filename):
        """Write the current Momentum script to an XML file

        Parameters
        ----------

        filename : string
            filename to be written to
        """
        outfile = open(filename, 'w')
        outfile.write(self.asXML())
        outfile.close()

    # UTILITY FUNCTIONS TO EDIT THE PYTHON REPRESENTATION
    #
    # might be replaced by something that only works on the xml scheme
    # for now this is easier

    def process_variables(self):
        """Returns the dict of process variables used in the Momentum script

        Returns
        -------
        variables : dict
            List of variables used in the script of the form `var_name : var_type` where var_type can be one of the allowed variable types in Momentum, e.g. String, Boolean, Date, ...

        See also
        --------

        profile_variables,
        """
        variables = self['process/variables']
        return {v['id']: v['type'] for v in variables}

    def profile_variables(self):
        """Returns the dict of profile variables used in the Momentum script. These are the ones given by momentum, independent of the actual script and cannot be changed.


        Returns
        -------
        variables : dict
            List of variables used in the script of the form `var_name : var_type` where var_type can be one of the allowed variable types in Momentum, e.g. String, Boolean, Date, ...

        See also
        --------

        process_variables, variables
        """
        variables = self['process/variables']
        return {v['id']: v['type'] for v in variables}

    def variables(self):
        """Returns the dict of all variables used in the Momentum script.

        Returns
        -------
        variables : dict
            List of variables used in the script of the form `var_name : var_type` where var_type can be one of the allowed variable types in Momentum, e.g. String, Boolean, Date, ...

        See also
        --------

        process_variables, profile_variables
        """
        return dict(self.process_variables(), **(self.profile_variables()))

    def add_container(self, name, container):
        """Adds a container to the set of containers used in the momentum script.

        Parameters
        ----------

        name : string
            name of the container. Will only be added if the name does not exist yet in the list of containers
        container : Container
            an object of components.containers.Container() that contains the specifications of the container
        """
        if name not in [c['id'] for c in self.containers]:
            self.containers.append(self.momentum_container(name, container))

    def add_variable(self, var, var_type='String'):
        """Add a variable to the process

        Parameters
        ----------
        var : string
            name of the variables. Will only be added if the variable does not exist yet
        var_type : string
            type of the variable. Default is `String`.
        """
        variables = self['process/variables']

        if var not in self.variables():
            variables.append(self.momentum_variable(var, var_type))

        self['process/variables'] = variables

    def rename_profile(self, name):
        """Renames the used profile. Should be used with care

        Notes
        -----

        For us this is always MSK, but maybe we want to use more profiles to have certain devices set on or off.
        """
        self['profile/id'] = name

    # CONVENIENCE ACCESSORS

    def clearsteps(self):
        """Removes all steps in the current script. This leaves a script that is valid, but does nothing.
        """
        self.steps = []

    @property
    def devices(self):
        """A shortcut to the devices in the profile. Replaces self['profile/devices']

        Returns
        -------

        devices : nested dict
            the dict of devices used

        """
        return self['profile/devices']

    @devices.setter
    def devices(self, value):
        self['profile/devices'] = value

    @property
    def steps(self):
        """A shortcut to the steps in the process. Replaces self['process/steps']

        Returns
        -------

        steps : nested dict
            the dict of steps

        """
        return self['process/steps']

    @steps.setter
    def steps(self, value):
        self['process/steps'] = value

    @property
    def containers(self):
        """A shortcut to the containers in the process. Replaces self['process/containers']

        Returns
        -------

        steps : nested dict
            the dict of containers

        """
        return self['process/containers']

    @containers.setter
    def containers(self, value):
        self['process/containers'] = value
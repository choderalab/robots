#==============================================================================
# GLOBAL IMPORTS
#==============================================================================

import simtk.unit as units

#==============================================================================
# SOLVENT
#==============================================================================


class Solvent(object):

    """
    A Solvent object represents a liquid that may be pipetted, and in which compounds may be dissolved.

    """

    def __init__(self, name, density=None):
        """
        Parameters
        ----------
        name : str
           The name of the solvent to create.
        density : simtk.unit.Quantity with units compatible with grams/milliliter, optional, default=None
           The density of the solvent.

        Examples
        --------

        Register a solvent.

        >>> water = Solvent('water', density=0.9970479*units.grams/units.centimeter**3)

        Register a solvent with density information.

        >>> dmso = Solvent('dmso', density=1.1004*units.grams/units.centimeter**3)

        """
        self.name = name
        self.density = density

#==============================================================================
# COMPOUND
#==============================================================================


class Compound(object):

    """
    A Compound object represents a compound that can be dissolved in a solvent.

    """

    def __init__(self, name, molecular_weight=None, purity=1.0):
        """
        Parameters
        ----------
        name : str
           The name of the compound to create.
        molecular_weight : simtk.unit.Quantity with units compatible with grams/mole, optional, default=None
           The molecular weight of the compound.
        purity : float, optional, default=1.0
           The mass purity used for computing actual quantity of compound.

        Examples
        --------

        Register a compound.

        >>> nacl = Compound('sodium chloride')

        Register a compound with molecular weight.

        >>> imatinib = Compound('imatinib mesylate', molecular_weight=589.7*units.grams/units.mole)

        Use a non-unit purity.

        >>> compound1 = Compound('compound1', molecular_weight=209.12*units.grams/units.mole, purity=0.975)

        """
        self.name = name
        self.molecular_weight = molecular_weight
        self.purity = purity


class PureLiquid(Compound):

    """A PureLiquid describes a pure liquid that can be part of a mixture of liquids."""

    def __init__(self, name, density, molecular_weight, purity=1.0):
        """
        name : str
            name of the liquid
        density : simtk.unit.Quantity with units compatible with grams/milliliter
            density of the pure liquid
        molecular weight : simtk.unit.Quantity with units compatible with grams/mole
            molecular weight of pure liquid
        purity : float, optional, default = 1.0
            fraction of liquid that is pure
        """
        super(
            PureLiquid,
            self).__init__(
            name,
            molecular_weight=molecular_weight,
            purity=purity)
        self.density = density

#==============================================================================
# SOLUTION
#==============================================================================


class SimpleSolution(Solvent):

    """
    A SimpleSolution object represents a solution containing one compound and one solvent.

    The solution is assumed to be ideal, with the same volume as that of the solvent.

    """

    def __init__(
            self,
            compound,
            compound_mass,
            solvent,
            solvent_mass,
            location):
        """
        compound : Compound
           The compound added to the solution.
        compound_mass : simtk.unit.Quantity compatible with grams
           The mass of compound added to the solution.
        solvent : Solvent
           The solvent used for the solution.
        solvent_mass : simtk.unit.Quantity compatible with grams
           The mass of solvent used for the solution.
        location : PipettingLocation
           The pipetting location holding the solution.

        Examples
        --------

        Create a simple salt solution.

        >>> salt = Compound('sodium chloride', molecular_weight=58.44277*units.grams/units.mole)
        >>> water = Solvent('water', density=0.9970479*units.grams/units.centimeter**3)
        >>> location = PipettingLocation('BufferTrough', 'Trough 100ml', 1)
        >>> solution = SimpleSolution(compound=salt, compound_mass=1.0*units.milligrams, solvent=water, solvent_mass=10.0*units.grams, location=location)

        TODO
        ----
        * Allow specification of quantity of compound and solvent in various ways (mass, moles, volume) with automated conversions.

        """

        self.compound = compound
        self.compound_mass = compound_mass
        self.solvent = solvent
        self.solvent_mass = solvent_mass

        self.name = compound.name

        # Compute total solution mass.
        self.solution_mass = self.compound_mass + self.solvent_mass

        # Assume solution is ideal; that density and volume is same as solvent.
        self.density = solvent.density
        self.volume = solvent_mass / solvent.density

        # Compute number of moles of compound.
        # number of moles of compound
        self.compound_moles = compound_mass / compound.molecular_weight * compound.purity

        # Compute molarity.
        self.concentration = self.compound_moles / self.volume

        # Store location.
        self.location = location


#==============================================================================
# MIXTURE
#==============================================================================

class SimpleMixture(Solvent):

    """
    A SimpleMixture object represents a solution containing a mixture of various solvents.

    The solution is assumed to be ideal, with the same volume as that of the solvent.

    """

    def __init__(
            self,
            components=list(),
            molefractions=list(),
            locations=list(),
            normalize_fractions=False):
        """
        components : list of PureLiquid
            components of the mixture
        molefractions : list of float
            mole fraction per component
        locations : list of PipettingLocation
            The pipetting location holding the pure liquids
        normalize_fractions : bool, optional, default = False
            Normalize any mole fractions to form a total of 1.
        """
        self.components = components
        self.molefractions = molefractions
        self.locations = locations
        # Consistency checks

        # Input length
        if not len(components) == len(molefractions) == len(locations):
            raise ValueError("Input lists do not have same length!")

        # Ensure total mole fraction equals 1
        if normalize_fractions:
            total = sum(self.molefractions)
            self.molefractions = map(lambda x: x / total, self.molefractions)
        else:
            # Check if mole fraction is 1 within arbitrary precision
            if abs(1.0 - sum(self.molefractions)) > 0.0001:
                raise ValueError("Total mole fractions out of bounds!")

        # Mass of compound relative to total mass
        self.massfractions = list()
        # Volume of compound relative to total volume (ideal solution
        # assumption)
        self.volumefractions = list()

        # Normalizing constant for molecular weight
        normalweight = sum(
            (comp.molecular_weight for comp in self.components),
            0 *
            units.grams /
            units.mole)
        # Normalizing constant for liquid density
        normaldens = sum(
            (comp.density for comp in self.components),
            0 *
            units.grams /
            units.milliliter)

        # Derive fractional masses from molecular weight
        for c, comp in enumerate(components):
            self.massfractions.append(
                self.molefractions[c] *
                comp.molecular_weight /
                normalweight)

        # Derive fractional volumes from mass and density
        for c, comp in enumerate(components):
            self.volumefractions.append(
                self.massfractions[c] *
                comp.density /
                normaldens)

    def __str__(self):
        """Represent a mixture by its composition."""
        return "<%s: %s>" % (self.__class__, self.describe())

    def describe(self):
        """Give a description of the mixture composition."""
        composition = str()
        for n, comp in enumerate(self.components):
            if self.molefractions[n] > 0.0:
                composition += comp.name
                composition += " %.2f" % self.molefractions[n]
                composition += "; "
        return composition

#==============================================================================
# MAIN AND TESTS
#==============================================================================

if __name__ == '__main__':
    import doctest
    doctest.testmod()

"""
Created on 14.04.2014

@author: Jan-Hendrik Prinz
"""

from klaatu.util import evo as ps


class WellSet(list):
    """
    A WellSet is a set of wells on one or more plates. Effectively this is a python list of Wells
    """

    def position_list(self):
        """
        Returns a list of positions of all the wells in the wellset
        """
        return [el._p for el in self]

    def well_list(self):
        """
        Returns a list of Well positions in the form [row, col] of all wells in the set
        """
        return [ps.PositionToWell(el.plate.dimensions, el._p) for el in self]

    def filter(self, query=":"):
        """
        Filters the WellSet according to a filter scheme and allows shifting of the wells.

        Parameters
        ----------

        query : string
            Filter string that is of the form `rows:cols` where rows and cols can have ranges indicated by `-` and have multiple definitions
            separated by `,`. Rows can be given by character or number. Default is `:` which returns all wells. Groups like this are separated
            by a `;`

        Notes
        -----
        Examples for the filters are `A-E:1-12` or `A,C,E:1-6` or `A-H-2:1-12-2;B-H-2:2-12-2` where the last one creates an alternating grid of wells.
        """
        parts = str.split(query.replace(' ', ''), ';')

        welllist = []

        for part in parts:
            rows = []
            cols = []
            if ':' in part:
                # extended list
                split = str.split(part, ':')
                left = split[0]
                right = split[1]

                for i in range(1, 17):
                    left = left.replace(chr(64 + i), str(i))

                leftparts = str.split(left, ',')
                for lpart in leftparts:
                    if '-' in lpart:
                        # range
                        split = str.split(lpart, '-')
                        if len(split) == 2:
                            rows.extend(range(int(split[0]), int(split[1]) + 1))
                        elif len(split) == 3:
                            rows.extend(range(int(split[0]), int(split[1]) + 1), int(split[2]))
                    else:
                        if len(lpart) > 0:
                            rows.extend([int(lpart)])

                rightparts = str.split(right, ',')
                for rpart in rightparts:
                    if '-' in rpart:
                        # range
                        split = str.split(rpart, '-')
                        if len(split) == 2:
                            cols.extend(range(int(split[0]), int(split[1]) + 1))
                        elif len(split) == 3:
                            cols.extend(range(int(split[0]), int(split[1]) + 1), int(split[2]))
                    else:
                        if len(rpart) > 0:
                            cols.extend([int(rpart)])
            else:
                if len(part) > 1:
                    rows = [ord(part[0]) - 64]
                    cols = [int(part[1:])]

            if len(cols) == 0:
                cols = range(1, 25)

            if len(rows) == 0:
                rows = range(1, 17)

            welllist.extend([[i, j] for i in rows for j in cols])

        wellnamelist = [ps.PositionToName(psr) for psr in welllist]

        return WellSet([psr for psr in self if ps.PositionToName(psr._p) in wellnamelist])

    def sort(self):
        """
        Returns a sorted version of the wellset.

        """
        return sorted(self, key=lambda x: x._p[1] * 100 + x._p[0])

    def apply(self, attr, fnc):
        return WellSet([getattr(element, attr)(attr(element)) for element in self])

    def mixture(self, mixtures):
        """
        Sets the mixture types for all wells in the wellset
        """

        def fnc(el):
            return mixtures[el.wellname()]

        return self.apply('setMixture', fnc)

    def plate(self, plate):
        """
        Sets the associated plate for all wells in the well set to a specific plate

        Parameters
        ----------

        plate : Plate
            The plate that the well should be associated to
        """

        return self.apply('set_plate', lambda x: plate)
"""field_fluid_description module"""

import numpy as np
import pandas as pd
import ecl2df

from pypvt import ElementFluidDescription


class FieldFluidDescription:
    """ A representation of black oil pvt and fluid contacts
    for a collection of fluid systems, ie a field.
    """

    def parse_case(self, case_name):
        eclfiles = ecl2df.EclFiles(case_name)
        grid = ecl2df.grid.df(eclfiles)
        pvt = ecl2df.pvt.df(eclfiles)
        equil = ecl2df.equil.df(eclfiles)

        return eclfiles, grid, pvt, equil

    def init_from_ecl(self, case):
        eclfiles, grid, pvt, equil = self.parse_case(case)
        top_struct = None
        bottom_struct = None
        if grid is not None:
            top_struct = grid["Z"].min()
            bottom_struct = grid["Z"].max()

        for pvtnr in pvt["PVTNUM"].unique():
            print("Processing pvtnum: ", pvtnr)
            for equilnr in grid[grid["PVTNUM"] == pvtnr]["EQLNUM"].unique():
                if grid is not None:
                    fluid = ElementFluidDescription(
                        eqlnum=equilnr,
                        pvtnum=pvtnr,
                        top_struct=top_struct,
                        bottom_struct=bottom_struct,
                    )
                else:
                    fluid = ElementFluidDescription(eqlnum=equilnr, pvtnum=pvtnr)
                fluid.init_from_ecl_pd(pvt, equil)
                self.fluid_descriptions.append(fluid)

    def validate_description(self):
        """
        Check if the minimum requirements of a fluid description is fulfilled:
        """

        for fluid in self.fluid_descriptions:
            if not fluid.validate_description():
                print(
                    "Fluid description of eqlnum region: ", fluid.eqlnum, " is invalid"
                )
                return False

        return True

    def __init__(self, ecl_case=None):
        self.fluid_descriptions = list([])  # why the fuck is this necessary ??
        self.max_depth = (10000,)
        self.min_depth = (0,)

        if ecl_case:
            self.init_from_ecl(ecl_case)

"""field_fluid_description module"""

import numpy as np
import pandas as pd
import copy
import sys

import ecl2df


from pypvt import ElementFluidDescription


class FieldFluidDescription:
    """ A representation of black oil pvt and fluid contacts
    for a collection of fluid systems, ie a field.
    """

    def parse_case(self, case_name):
        eclfiles = ecl2df.EclFiles(case_name)
        dataframes = {}
        try:
            dataframes['GRID'] = ecl2df.grid.df(eclfiles)
        except:
            dataframes['GRID'] = None

        try:
            dataframes['PVT'] = ecl2df.pvt.df(eclfiles)
        except:
            dataframes['PVT'] = None

        try:
            dataframes['EQUIL'] = ecl2df.equil.df(eclfiles, keywords='EQUIL')
        except:
            dataframes['EQUIL'] = None

        try:
            dataframes['RSVD'] = ecl2df.equil.df(eclfiles, keywords='RSVD')
        except:
            dataframes['RSVD'] = None

        try:
            dataframes['RVVD'] = ecl2df.equil.df(eclfiles, keywords='RVVD')
        except:
            dataframes['RVVD'] = None


        return eclfiles, dataframes

    def init_from_ecl(self, case):
        eclfiles, eclkw_dict = self.parse_case(case)

        grid = None
        try:
            grid = eclkw_dict['GRID']
        except:
            print ('No grid found, exiting')
            sys.exit()

        top_struct = None
        bottom_struct = None
        if eclkw_dict['GRID'] is not None:
            top_struct = grid["Z"].min()
            bottom_struct = grid["Z"].max()

        pvt = None
        try:
            pvt = eclkw_dict['PVT']
        except:
            print ('No pvt found, exiting')
            sys.exit()



        fluid_index = 0
        for pvtnr in pvt["PVTNUM"].unique():
            print("Processing pvtnum: ", pvtnr)
            for equilnr in grid[grid["PVTNUM"] == pvtnr]["EQLNUM"].unique():
                if grid is not None:
                    fluid = ElementFluidDescription(
                        eqlnum=int(equilnr),
                        pvtnum=int(pvtnr),
                        top_struct=top_struct,
                        bottom_struct=bottom_struct,
                    )
                else:
                    fluid = ElementFluidDescription(
                        eqlnum=int(equilnr), pvtnum=int(pvtnr)
                    )
                fluid.init_from_ecl_df(eclkw_dict)
                self.fluid_descriptions.append(fluid)
                self.fluid_index[int(equilnr)] = fluid_index
                fluid_index += 1

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

    def set_owc(self, eqlnum, owc):
        new_self = copy.deepcopy(self)
        new_self.fluid_descriptions[self.fluid_index[eqlnum]] = self.fluid_descriptions[
            self.fluid_index[eqlnum]
        ].set_owc(owc)
        return new_self

    def set_goc(self, eqlnum, goc):
        new_self = copy.deepcopy(self)
        new_self.fluid_descriptions[self.fluid_index[eqlnum]] = self.fluid_descriptions[
            self.fluid_index[eqlnum]
        ].set_goc(owc)
        return new_self

    def __init__(self, ecl_case=None):
        self.fluid_descriptions = list([])
        self.fluid_index = {}
        self.max_depth = (10000,)
        self.min_depth = (0,)

        if ecl_case:
            self.init_from_ecl(ecl_case)

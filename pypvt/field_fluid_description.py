"""field_fluid_description module"""

import numpy as np
import pandas as pd
import ecl2df

from pypvt import element_fluid_description

class  field_fluid_description:
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
        for pvtnr in pvt['PVTNUM'].unique():
            print ('Processing pvtnum: ', pvtnr)
            for equilnr in grid[grid['PVTNUM']==pvtnr]['EQLNUM'].unique():
                fluid = element_fluid_description.element_fluid_description(eqlnum=equilnr,pvtnum=pvtnr)
                fluid.init_from_ecl_pd(pvt, equil)
                self.fluid_descriptions.append(fluid)


    def validate_description (self):
        """
        Check if the minimum requirements of a fluid description is fulfilled:
        """

        for fluid in self.fluid_descriptions:
            if not fluid.validate_description():
                print ('Fluid description of eqlnum region: ', fluid.eqlnum, ' is invalid')
                return False

        return True



    def __init__ (self,ecl_case = None):
        self.fluid_descriptions = list([]) # why the fuck is this necessary ??
        self.max_depth = 10000,
        self.min_depth = 0,

        if ecl_case:
            self.init_from_ecl(ecl_case)

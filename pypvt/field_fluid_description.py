"""field_fluid_description module"""

import sys
import copy

import pandas as pd
import ecl2df

from .element_fluid_description import ElementFluidDescription


class FieldFluidDescription:
    """ A representation of black oil pvt and fluid contacts
    for a collection of fluid systems, ie a field.
    """

    def __init__(self, ecl_case=None):
        self.fluid_descriptions = list([])
        self.inactive_fluid_descriptions = list([])
        self.fluid_index = {}
        self.inacive_fluid_index = {}
        self.max_depth = (10000,)
        self.min_depth = (0,)

        if ecl_case:
            self.init_from_ecl(ecl_case)

    @staticmethod
    def _parse_case(case_name):
        eclfiles = ecl2df.EclFiles(case_name)
        dataframes = {}

        dataframes["GRID"] = ecl2df.grid.df(eclfiles)
        dataframes["PVT"] = ecl2df.pvt.df(eclfiles)
        dataframes["EQUIL"] = ecl2df.equil.df(eclfiles, keywords="EQUIL")
        dataframes["RSVD"] = ecl2df.equil.df(eclfiles, keywords="RSVD")
        dataframes["RVVD"] = ecl2df.equil.df(eclfiles, keywords="RVVD")

        return dataframes

    def init_from_ecl(self, case):
        ecldf_dict = FieldFluidDescription._parse_case(case)

        grid = None
        try:
            grid = ecldf_dict["GRID"]
        except KeyError:
            print("No grid found, exiting")
            sys.exit()

        top_struct = None
        bottom_struct = None
        if ecldf_dict["GRID"] is not None:
            top_struct = grid["Z"].min()
            bottom_struct = grid["Z"].max()

        pvt = None
        try:
            pvt = ecldf_dict["PVT"]
        except KeyError:
            print("No pvt found, exiting")
            sys.exit()

        equil = None
        try:
            equil = ecldf_dict["EQUIL"]
        except KeyError:
            print("No equil found, exiting")
            sys.exit()

        fluid_index = 0
        for pvtnr in pvt["PVTNUM"].unique():
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
                fluid.init_from_ecl_df(ecldf_dict)
                self.fluid_descriptions.append(fluid)
                self.fluid_index[int(equilnr)] = fluid_index
                fluid_index += 1

        fluid_index = 0
        inactive_equils = list(
            set(equil["EQLNUM"].unique()) - set(self.fluid_index.keys())
        )
        for equilnr in inactive_equils:
            fluid = ElementFluidDescription(
                eqlnum=int(equilnr), pvtnum=len(pvt["PVTNUM"].unique())
            )
            fluid.init_from_ecl_df(ecldf_dict)
            self.inactive_fluid_descriptions.append(fluid)
            self.inacive_fluid_index[int(equilnr)] = fluid_index
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
        ].set_goc(goc)
        return new_self

    def get_df(self, keyword):
        """
        retrun: pandas.df according to the requested keyword
        supported: equil, rsvd, rvvd, pbvd, pdvd, and the pvt related kws
        """

        dataframe = pd.DataFrame(columns=["EQLNUM", "OWC", "GOC"])
        for fluid in self.fluid_descriptions:
            dataframe = pd.merge(
                left=dataframe, right=fluid.get_df(keyword), how="outer"
            )
        for fluid in self.inactive_fluid_descriptions:
            dataframe = pd.merge(
                left=dataframe, right=fluid.get_df(keyword), how="outer"
            )

        return dataframe

    def write_equilkws(self, keywords, filename):
        """
        Write kws equil, rsvd, rvvd, pbvd, pdvd to file
        """

        comments = {}
        dframe = None

        if "EQUIL" in keywords:
            if dframe is None:
                dframe = self.get_df("EQUIL")
            else:
                dframe = pd.merge(left=dframe, right=self.get_df("EQUIL"), how="outer")
            comments["EQUIL"] = "EQUIL kw created by pypvt"

        ecl2df.equil.df2ecl(
            dframe, keywords=keywords, comments=comments, filename=filename
        )

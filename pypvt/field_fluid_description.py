"""field_fluid_description module"""

import logging

from typing import List
import sys
import copy

import pandas as pd
import ecl2df

from pypvt.element_fluid_description import ElementFluidDescription

# pylint: disable=too-many-branches


# A new handler to store "raw" LogRecords instances
class RecordsListHandler(logging.Handler):
    """
    A handler class which stores LogRecord entries in a list
    """

    def __init__(self, r_list):
        """
        Initiate the handler
        :param records_list: a list to store the LogRecords entries
        """
        self.records_list = r_list
        super().__init__()

    def emit(self, record):
        self.records_list.append(record)


class FieldFluidDescription:
    """A representation of black oil pvt and fluid contacts
    for a collection of fluid systems, ie a field.
    """

    def __init__(self, ecl_case=None):
        self.fluid_descriptions = list([])
        self.inactive_fluid_descriptions = list([])
        self.fluid_index = {}
        self.inacive_fluid_index = {}
        self.max_depth = (10000,)
        self.min_depth = (0,)

        self._records_list = []
        self._pvt_logger = logging.getLogger(__name__)
        self._pvt_logger.addHandler(RecordsListHandler(self._records_list))

        if ecl_case:
            self.init_from_ecl(ecl_case)

    @property
    def logger(self):
        return self._pvt_logger

    def records_list(self):
        return self._records_list

    @staticmethod
    def _parse_case(case_name):
        eclfiles = ecl2df.EclFiles(case_name)
        dataframes = {}

        dataframes["GRID"] = ecl2df.grid.df(eclfiles)
        dataframes["PVT"] = ecl2df.pvt.df(eclfiles)
        dataframes["EQUIL"] = ecl2df.equil.df(eclfiles, keywords="EQUIL")
        dataframes["RSVD"] = ecl2df.equil.df(eclfiles, keywords="RSVD")
        dataframes["RVVD"] = ecl2df.equil.df(eclfiles, keywords="RVVD")
        dataframes["PBVD"] = ecl2df.equil.df(eclfiles, keywords="PBVD")
        dataframes["PDVD"] = ecl2df.equil.df(eclfiles, keywords="PDVD")

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
                        pvt_logger=self.logger,
                    )
                else:
                    fluid = ElementFluidDescription(
                        eqlnum=int(equilnr),
                        pvtnum=int(pvtnr),
                        pvt_logger=self.logger,
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

    def write_equilkws(self, keywords: List[str], filename: str) -> None:
        """
        Write keywords equil, rsvd, rvvd, pbvd, pdvd to file

        Args:
            keywords: List of keywords to export.
            filename: Filename to export keywords to

        Returns:
            None

        """
        comments = {}
        dframe = None
        lookup_keywords = ["EQUIL", "RSVD", "RVVD", "PBVD", "PDVD"]

        for keyword in lookup_keywords:

            if keyword in keywords:
                if dframe is None:
                    dframe = self.get_df(keyword)
                else:
                    dframe = pd.merge(left=dframe, right=self.get_df(keyword))
                comments[keyword] = f"{keyword} kw created by pypvt"

        ecl2df.equil.df2ecl(
            dframe, keywords=keywords, comments=comments, filename=filename
        )

    def create_consistency_report(self):
        def filter_records(records, rtype, pvtnum):
            selection = []
            for record in records:
                if (
                    record.__dict__["levelname"] == rtype
                    and record.__dict__.get("pvtnum", None) == pvtnum
                ):
                    selection.append(record)
            return selection

        records = self.records_list()
        print("***********************************************************")
        print("*****             PVT consistency report               ****")
        print("*****                                                  ****")
        print()
        print(
            "This model has ",
            len(self.fluid_descriptions),
            " active equli regions and ",
            len(self.inactive_fluid_descriptions),
            " inactive",
        )
        print()
        for fluid in self.fluid_descriptions:
            print("***********************************************************")
            print("EQUIL nr: ", fluid.eqlnum, " PVTNUM:", fluid.pvtnum)

            warnings = filter_records(records, "WARNING", fluid.pvtnum)
            print("WARNINGS: ", len(warnings))
            for record in warnings:
                print("  ", record.__dict__["msg"])

            errors = filter_records(records, "ERROR", fluid.pvtnum)
            print("ERRORS: ", len(errors))
            for record in errors:
                print("  ", record.__dict__["msg"])

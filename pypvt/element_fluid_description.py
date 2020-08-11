"""element_fluid_description module"""

import numpy as np
import pandas as pd


class ElementFluidDescription:
    """ A representation of black oil pvt and fluid contacts
    for a fluid system, valid for one specific equil number
    in an eclipse simulation deck.
    """

    def __init__(
        self, eqlnum=0, pvtnum=0, top_struct=0, bottom_struct=10000, ecl_case=None,
    ):
        self.pvtnum = pvtnum
        self.eqlnum = eqlnum

        self.owc = None
        self.goc = None

        self.ref_depth = None
        self.ref_press = None

        self.top_struct = top_struct
        self.bottom_struct = bottom_struct

        self.rsvd_rs = None
        self.rsvd_depth = None

        self.rvvd_rs = None
        self.rvvd_depth = None

        # self.pvto_o = None # 2D som ecl2df dataframe (trykk; mettet og umettet)
        # self.pvto_press = None
        # self.pvtg_bg = None
        # self.pvtg_press = None

    def init_from_ecl_df(self, pvt_df, eql_df):
        self.owc = eql_df[eql_df["EQLNUM"] == self.eqlnum]["OWC"].unique()[0]
        self.goc = eql_df[eql_df["EQLNUM"] == self.eqlnum]["GOC"].unique()[0]

        self.ref_depth = eql_df[
            (eql_df["EQLNUM"] == self.eqlnum) & (eql_df["KEYWORD"] == "EQUIL")
        ]["Z"].unique()[0]
        self.ref_press = eql_df[
            (eql_df["EQLNUM"] == self.eqlnum) & (eql_df["KEYWORD"] == "EQUIL")
        ]["PRESSURE"].unique()[0]

        self.rsvd_rs = eql_df[
            (eql_df["EQLNUM"] == self.eqlnum) & (eql_df["RS"].notnull())
        ]["RS"].to_numpy()
        self.rsvd_depth = eql_df[
            (eql_df["EQLNUM"] == self.eqlnum) & (eql_df["RS"].notnull())
        ]["Z"].to_numpy()

        self.rvvd_rv = eql_df[
            (eql_df["EQLNUM"] == self.eqlnum) & (eql_df["RV"].notnull())
        ]["RV"].to_numpy()
        self.rvvd_depth = eql_df[
            (eql_df["EQLNUM"] == self.eqlnum) & (eql_df["RV"].notnull())
        ]["Z"].to_numpy()

    def validate_description(self):
        """
        check if the minimum requirements of a fluid description is fulfilled:

        """
        if not self.eqlnum:
            print("EQILNUM not defined")
            return False

        if not self.pvtnum:
            print("PVTNUM not defined")
            return False

        if not self.owc:
            print("OWC not defined")
            return False

        if not self.goc:
            print("GOC not defined")
            return False

        if not self.ref_depth:
            print("ref_depth not defined")
            return False

        if not self.ref_press:
            print("ref_press not defined")
            return False

        if not self.top_struct:
            print("top_struct not defined")
            return False

        if not self.bottom_struct:
            print("bottom_struct not defined")

        if self.rsvd_rs is None:
            print("RSVD not defined")
            return False

        if self.rsvd_depth is None:
            print("RSVD not defined")
            return False

        if self.rvvd_rv is None:
            print("RVVD not defined")
            return False

        if self.rvvd_depth is None:
            print("RVVD not defined")
            return False

        return True

    def get_bo(press, rs):
        pass

    def get_rs(p_bub):
        pass

    def get_p_bub(rs):
        pass

    def get_visc_oil(press, rs):
        pass

    def get_visc_gas(press, rs):
        pass

    def get_bg(press, rv):
        pass

    def get_bv(p_dew):
        pass

    def calc_den_oil(press, bo, rs, rv):
        pass

    def calc_den_gas(press, bg, rs, rv):
        pass

    def res_press_gradient():
        pass

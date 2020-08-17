"""element_fluid_description module"""

import copy

import pandas as pd


# pylint: disable=too-many-instance-attributes
class ElementFluidDescription:

    """ A representation of black oil pvt and fluid contacts
    for a fluid system, valid for one specific equil number
    in an eclipse simulation deck.
    """

    def __init__(
        self, eqlnum=0, pvtnum=0, top_struct=0, bottom_struct=10000, ecl_case=None,
    ):

        self.ecl_case = ecl_case

        self.original = None
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

        self.rvvd_rv = None
        self.rvvd_depth = None

        # self.pvto_o = None # 2D som ecl2df dataframe (trykk; mettet og umettet)
        # self.pvto_press = None
        # self.pvtg_bg = None
        # self.pvtg_press = None

    # pylint: disable=attribute-defined-outside-init
    def init_equil_from_df(self, eql_df):
        """
        Set owc, goc, ref depth, ref press, pcowc, pcgoc, initrs, initrv, accuracy
        from an ecl2df.equil_df object
        """

        self.owc = eql_df[eql_df["EQLNUM"] == self.eqlnum]["OWC"].unique()[0]
        self.goc = eql_df[eql_df["EQLNUM"] == self.eqlnum]["GOC"].unique()[0]
        self.pcowc = eql_df[eql_df["EQLNUM"] == self.eqlnum]["PCOWC"].unique()[0]
        self.pcgoc = eql_df[eql_df["EQLNUM"] == self.eqlnum]["PCGOC"].unique()[0]
        self.initrs = eql_df[eql_df["EQLNUM"] == self.eqlnum]["INITRS"].unique()[0]
        self.initrv = eql_df[eql_df["EQLNUM"] == self.eqlnum]["INITRV"].unique()[0]
        self.accuracy = eql_df[eql_df["EQLNUM"] == self.eqlnum]["ACCURACY"].unique()[0]

        self.ref_depth = eql_df[
            (eql_df["EQLNUM"] == self.eqlnum) & (eql_df["KEYWORD"] == "EQUIL")
        ]["Z"].unique()[0]
        self.ref_press = eql_df[
            (eql_df["EQLNUM"] == self.eqlnum) & (eql_df["KEYWORD"] == "EQUIL")
        ]["PRESSURE"].unique()[0]

    def init_rsvd_from_df(self, rsvd_df):
        """
        Set rsvd, from an ecl2df.equil_df object
        """
        self.rsvd_rs = rsvd_df[
            (rsvd_df["EQLNUM"] == self.eqlnum) & (rsvd_df["RS"].notnull())
        ]["RS"].to_numpy()
        self.rsvd_depth = rsvd_df[
            (rsvd_df["EQLNUM"] == self.eqlnum) & (rsvd_df["RS"].notnull())
        ]["Z"].to_numpy()

    def init_rvvd_from_df(self, rvvd_df):
        """
        Set rvvd, from an ecl2df.equil_df object
        """
        self.rvvd_rv = rvvd_df[
            (rvvd_df["EQLNUM"] == self.eqlnum) & (rvvd_df["RV"].notnull())
        ]["RV"].to_numpy()
        self.rvvd_depth = rvvd_df[
            (rvvd_df["EQLNUM"] == self.eqlnum) & (rvvd_df["RV"].notnull())
        ]["Z"].to_numpy()

    def init_pvt_from_df(self, pvt_df):
        """
        Set pvt, from an ecl2df.equil_df object
        """
        raise NotImplementedError

    def init_from_ecl_df(self, df_dict):
        if "PCGOC" in df_dict["EQUIL"].keys():
            self.init_equil_from_df(df_dict["EQUIL"])

        if "PVT" in df_dict["PVT"].keys():
            self.init_pvt_from_df(df_dict["PVT"])

        if "RSVD" in df_dict["RSVD"].keys():
            self.init_rsvd_from_df(df_dict["RSVD"])

        if "RVVD" in df_dict["RVVD"].keys():
            self.init_rvvd_from_df(df_dict["RVVD"])

    def validate_description(self):
        # pylint: disable=too-many-return-statements
        """
        check if the minimum requirements of a fluid description is fulfilled:

        """
        if not self.eqlnum:
            print("EQILNUM not defined")
            return False

        if not self.pvtnum:
            print("PVTNUM not defined")
            return False

        if self.owc is None:
            print("OWC not defined")
            print(self.owc)
            return False

        if self.goc is None:
            print("GOC not defined")
            return False

        if self.ref_depth is None:
            print("ref_depth not defined")
            return False

        if self.ref_press is None:
            print("ref_press not defined")
            return False

        if self.top_struct is None:
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

    def get_bo(self, press, rs) -> float:
        raise NotImplementedError

    def get_rs(self, p_bub) -> float:
        raise NotImplementedError

    def get_p_bub(self, rs) -> float:
        raise NotImplementedError

    def get_visc_oil(self, press, rs) -> float:
        raise NotImplementedError

    def get_visc_gas(self, press, rs) -> float:
        raise NotImplementedError

    def get_bg(self, press, rv) -> float:
        raise NotImplementedError

    def get_bv(self, p_dew) -> float:
        raise NotImplementedError

    def calc_den_oil(self, press, bo, rs, rv) -> float:
        raise NotImplementedError

    def calc_den_gas(self, press, bg, rs, rv) -> float:
        raise NotImplementedError

    def res_press_gradient(self) -> float:
        raise NotImplementedError

    def set_owc(self, owc):
        new_self = copy.deepcopy(self)
        new_self.owc = owc
        return new_self

    def set_goc(self, goc):
        new_self = copy.deepcopy(self)
        new_self.goc = goc
        return new_self

    def get_df(self, keyword):
        """
        returns: pandas.Dataframe for specified keyword
        """

        df = None

        if keyword == "EQUIL":

            df = pd.DataFrame(
                columns=[
                    "KEYWORD",
                    "EQLNUM",
                    "OWC",
                    "PCOWC",
                    "GOC",
                    "PCGOC",
                    "Z",
                    "PRESSURE",
                    "INITRS",
                    "INITRV",
                    "ACCURACY",
                ]
            )

            df = df.append(
                {
                    "KEYWORD": "EQUIL",
                    "EQLNUM": self.eqlnum,
                    "OWC": self.owc,
                    "PCOWC": self.pcowc,
                    "GOC": self.goc,
                    "PCGOC": self.pcgoc,
                    "Z": self.ref_depth,
                    "PRESSURE": self.ref_press,
                    "INITRS": self.initrs,
                    "INITRV": self.initrv,
                    "ACCURACY": self.accuracy,
                },
                ignore_index=True,
            )

        elif keyword == "RSVD":
            pass
        elif keyword == "RVVD":
            pass
        elif keyword == "BPVD":
            pass
        elif keyword == "DPVD":
            pass
        else:
            print("No supprt for keyword:", keyword)

        return df

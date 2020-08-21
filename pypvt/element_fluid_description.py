"""element_fluid_description module"""

import copy

import pandas as pd
import numpy as np

from .bopvt import BoPVT

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=invalid-name
# pylint: disable=too-many-locals
# pylint: disable=expression-not-assigned
class ElementFluidDescription:

    """ A representation of black oil pvt and fluid contacts
    for a fluid system, valid for one specific equil number
    in an eclipse simulation deck.
    """

    def __init__(
        self, eqlnum=0, pvtnum=0, top_struct=0, bottom_struct=10000, ecl_case=None,
    ):

        self.ecl_case = ecl_case

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

        self.pbvd_pb = None
        self.pbvd_depth = None

        self.pdvd_pd = None
        self.pdvd_depth = None

        self.pvt_model = BoPVT(self.pvtnum)

        self.res_depth = []
        self.res_fluid_type = []
        self.res_pres = []
        self.res_psat = []
        self.res_pbub = []
        self.res_pdew = []
        self.res_den = []
        self.res_deng = []
        self.res_deno = []
        self.res_denw = []
        self.res_gor = []
        self.res_rs = []
        self.res_rv = []
        self.res_bo = []
        self.res_bg = []
        self.res_bw = []
        self.res_viso = []
        self.res_visg = []
        self.res_visw = []

    @staticmethod
    def intpol(x, xt, yt, extpol_opt="const", order="ascending"):
        """
        Under construction!
        Should potentially figure out extrapolation, and x-table
        monotonicity stuff

        Linear interpolation

        """

        if extpol_opt != "const":
            raise ValueError("extpol_opt not implemented")

        if order != "ascending":
            raise ValueError("order not implemented")

        # A quick and dirty version for now
        y = np.interp(x, xt, yt)

        return y

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

    def init_pbvd_from_df(self, pbvd_df):
        """
        Set pbvd, from an ecl2df.equil_df object
        """

        self.pbvd_pb = pbvd_df[
            (pbvd_df["EQLNUM"] == self.eqlnum) & (pbvd_df["PB"].notnull())
        ]["PB"].to_numpy()
        self.pbvd_depth = pbvd_df[
            (pbvd_df["EQLNUM"] == self.eqlnum) & (pbvd_df["PB"].notnull())
        ]["Z"].to_numpy()

    def init_pdvd_from_df(self, pdvd_df):
        """
        Set pdvd, from an ecl2df.equil_df object
        """

        self.pdvd_pd = pdvd_df[
            (pdvd_df["EQLNUM"] == self.eqlnum) & (pdvd_df["PD"].notnull())
        ]["PD"].to_numpy()
        self.pdvd_depth = pdvd_df[
            (pdvd_df["EQLNUM"] == self.eqlnum) & (pdvd_df["PD"].notnull())
        ]["Z"].to_numpy()

    def init_pvt_from_df(self, pvt_df):
        """
        Set pvt, from an ecl2df.equil_df object
        """
        raise NotImplementedError

    def init_from_ecl_df(self, df_dict):
        if not df_dict["EQUIL"].empty:
            self.init_equil_from_df(df_dict["EQUIL"])

        if not df_dict["RSVD"].empty:
            self.init_rsvd_from_df(df_dict["RSVD"])

        if not df_dict["RVVD"].empty:
            self.init_rvvd_from_df(df_dict["RVVD"])

        if not df_dict["PBVD"].empty:
            self.init_pbvd_from_df(df_dict["PBVD"])

        if not df_dict["PDVD"].empty:
            self.init_pdvd_from_df(df_dict["PDVD"])

        if not df_dict["PVT"].empty:
            pvt_df = df_dict["PVT"]

            if "PVTO" in pvt_df["KEYWORD"].unique():
                self.pvt_model.set_pvto_from_df(
                    pvt_df[pvt_df["KEYWORD"] == "PVTO"][
                        ["RS", "PRESSURE", "VOLUMEFACTOR", "OILDENSITY", "PVTNUM"]
                    ]
                )
            else:
                raise ValueError("PVTO not found in PVT dataframe")

            if "PVTG" in pvt_df["KEYWORD"].unique():
                self.pvt_model.set_pvtg_from_df(
                    pvt_df[pvt_df["KEYWORD"] == "PVTG"][
                        ["PRESSURE", "OGR", "VOLUMEFACTOR", "VISCOSITY", "PVTNUM"]
                    ]
                )
            else:
                raise ValueError("PVTG not found in PVT dataframe")

            if "PVTW" in pvt_df["KEYWORD"].unique():
                self.pvt_model.set_pvtw_from_df(
                    pvt_df[pvt_df["KEYWORD"] == "PVTW"][
                        [
                            "PRESSURE",
                            "VOLUMEFACTOR",
                            "COMPRESSIBILITY",
                            "VISCOSITY",
                            "VISCOSIBILITY",
                            "PVTNUM",
                        ]
                    ]
                )
            else:
                raise ValueError("PVTW not found in PVT dataframe")

            if "DENSITY" in pvt_df["KEYWORD"].unique():
                self.pvt_model.set_densities_from_df(
                    pvt_df[pvt_df["KEYWORD"] == "DENSITY"][
                        ["OILDENSITY", "GASDENSITY", "WATERDENSITY", "PVTNUM"]
                    ]
                )
            else:
                raise ValueError("DENSITY not found in PVT dataframe")

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

        if self.rvvd_rv is None and self.rsvd_rs is None:
            if self.pbvd_depth is None:
                print("PBVD not defined")
                return False

            if self.pbvd_pb is None:
                print("PBVD not defined")
                return False

            if self.pdvd_depth is None:
                print("PDVD not defined")
                return False

            if self.pdvd_pd is None:
                print("PDVD not defined")
                return False
        else:
            if self.rsvd_depth is None:
                print("RSVD depth not defined")
                return False

            if self.rsvd_rs is None:
                print("RSVD not defined")
                return False

            if self.rvvd_depth is None:
                print("RVVD depth not defined")
                return False

            if self.rvvd_rv is None:
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
            df = pd.DataFrame(columns=["KEYWORD", "EQLNUM", "RS", "Z"])

            for i in range(len(self.rsvd_rs)):
                df = df.append(
                    {
                        "KEYWORD": "RSVD",
                        "EQLNUM": self.eqlnum,
                        "RS": self.rsvd_rs[i],
                        "Z": self.rsvd_depth[i],
                    },
                    ignore_index=True,
                )

        elif keyword == "RVVD":
            df = pd.DataFrame(columns=["KEYWORD", "EQLNUM", "RV", "Z"])

            for i in range(len(self.rvvd_rv)):
                df = df.append(
                    {
                        "KEYWORD": "RVVD",
                        "EQLNUM": self.eqlnum,
                        "RV": self.rvvd_rv[i],
                        "Z": self.rvvd_depth[i],
                    },
                    ignore_index=True,
                )

        elif keyword == "PBVD":
            df = pd.DataFrame(columns=["KEYWORD", "EQLNUM", "PB", "Z"])

            for i in range(len(self.pbvd_pb)):
                df = df.append(
                    {
                        "KEYWORD": "PBVD",
                        "EQLNUM": self.eqlnum,
                        "PB": self.pbvd_pb[i],
                        "Z": self.pbvd_depth[i],
                    },
                    ignore_index=True,
                )

        elif keyword == "PDVD":
            df = pd.DataFrame(columns=["KEYWORD", "EQLNUM", "PD", "Z"])

            for i in range(len(self.pdvd_pd)):
                df = df.append(
                    {
                        "KEYWORD": "PDVD",
                        "EQLNUM": self.eqlnum,
                        "PD": self.pdvd_pd[i],
                        "Z": self.pdvd_depth[i],
                    },
                    ignore_index=True,
                )
        else:
            print("No supprt for keyword:", keyword)

        return df

    # -----------------------------------------------------------------------------
    def calc_fluid_prop_vs_depth(self, no_nodes=20):
        """ Calculates fluid properties vs. depth """

        # ---------------------------------------------------------------------
        # Calculate properties from REFERENCE depth to TOP reservoir
        # ---------------------------------------------------------------------

        GD = 0.0981 / 1000.0  #  [m]*[kg/m3] -> [bar]

        goc = self.goc
        woc = self.owc

        top = self.top_struct
        bottom = self.bottom_struct
        delta_d = (bottom - top) / no_nodes

        d = self.ref_depth
        p = self.ref_press

        while d > top - delta_d:

            # Calculate fluid properties at current node
            rs = self.intpol(d, self.rsvd_depth, self.rsvd_rs)
            rv = self.intpol(d, self.rvvd_depth, self.rvvd_rv)

            pbub = self.pvt_model.calc_pbub(rs)

            if pbub < p:
                bo = self.pvt_model.calc_bo(p, rs=rs)
                deno = self.pvt_model.calc_deno(p, rs=rs)
                viso = self.pvt_model.calc_viso(p, rs=rs)

            else:
                bo = self.pvt_model.calc_bo(p)
                deno = self.pvt_model.calc_deno(p)
                viso = self.pvt_model.calc_viso(p)

            pdew = self.pvt_model.calc_pdew(rv)

            if pdew < p:
                bg = self.pvt_model.calc_bg(p, rv=rv)
                deng = self.pvt_model.calc_deng(p, rv=rv)
                visg = self.pvt_model.calc_visg(p, rv=rv)

            else:
                bg = self.pvt_model.calc_bg(p)
                deng = self.pvt_model.calc_deng(p)
                visg = self.pvt_model.calc_visg(p)

            bw = self.pvt_model.calc_bw(p)
            denw = self.pvt_model.calc_denw(p)
            visw = self.pvt_model.calc_visw(p)

            # Determine correct phase
            if d <= goc:
                fluid_type = "gas"
                psat = pdew
                gor = 1.0 / rv
                den = deng

            elif d > woc:
                fluid_type = "wat"
                psat = pbub
                den = denw
                gor = rs

            else:
                fluid_type = "oil"
                psat = pbub
                den = deno
                gor = rs

            # Set depth node fluid properties

            self.res_depth.append(d)
            self.res_fluid_type.append(fluid_type)
            self.res_pres.append(p)
            self.res_psat.append(psat)
            self.res_pbub.append(pbub)
            self.res_pdew.append(pdew)
            self.res_den.append(den)
            self.res_deng.append(deng)
            self.res_deno.append(deno)
            self.res_denw.append(denw)
            self.res_gor.append(gor)
            self.res_rs.append(rs)
            self.res_rv.append(rv)
            self.res_bo.append(bo)
            self.res_bg.append(bg)
            self.res_bw.append(bw)
            self.res_viso.append(viso)
            self.res_visg.append(visg)
            self.res_visw.append(visw)

            # Update node depth
            d_next = d - delta_d

            if abs(d_next - goc) < delta_d:
                d_next = goc
            if abs(d_next - woc) < delta_d:
                d_next = woc

            # Update new node pressure
            p = p + GD * den * (d_next - d)

            d = d_next

        # ---------------------------------------------------------------------
        # Calculate properties from REFERENCE depth to BOTTOM reservoir
        # ---------------------------------------------------------------------

        # Reverse depth lists, so top node is first element
        self.res_depth.reverse()
        self.res_fluid_type.reverse()
        self.res_pres.reverse()
        self.res_psat.reverse()
        self.res_pbub.reverse()
        self.res_pdew.reverse()
        self.res_den.reverse()
        self.res_deng.reverse()
        self.res_deno.reverse()
        self.res_denw.reverse()
        self.res_gor.reverse()
        self.res_rs.reverse()
        self.res_rv.reverse()
        self.res_bo.reverse()
        self.res_bg.reverse()
        self.res_bw.reverse()
        self.res_viso.reverse()
        self.res_visg.reverse()
        self.res_visw.reverse()

        d = self.ref_depth
        d_next = d + delta_d
        if abs(d_next - goc) < delta_d:
            d_next = goc
        if abs(d_next - woc) < delta_d:
            d_next = woc

        p = self.ref_press + GD * self.res_den[-1] * (d_next - d)
        d = d_next

        while d < bottom + delta_d:

            # Calculate fluid properties at current node
            rs = self.intpol(d, self.rsvd_depth, self.rsvd_rs)
            rv = self.intpol(d, self.rvvd_depth, self.rvvd_rv)

            pbub = self.pvt_model.calc_pbub(rs)

            if pbub < p:
                bo = self.pvt_model.calc_bo(p, rs=rs)
                deno = self.pvt_model.calc_deno(p, rs=rs)
                viso = self.pvt_model.calc_viso(p, rs=rs)

            else:
                bo = self.pvt_model.calc_bo(p)
                deno = self.pvt_model.calc_deno(p)
                viso = self.pvt_model.calc_viso(p)

            pdew = self.pvt_model.calc_pdew(rv)

            if pdew < p:
                bg = self.pvt_model.calc_bg(p, rv=rv)
                deng = self.pvt_model.calc_deng(p, rv=rv)
                visg = self.pvt_model.calc_visg(p, rv=rv)

            else:
                bg = self.pvt_model.calc_bg(p)
                deng = self.pvt_model.calc_deng(p)
                visg = self.pvt_model.calc_visg(p)

            bw = self.pvt_model.calc_bw(p)
            denw = self.pvt_model.calc_denw(p)
            visw = self.pvt_model.calc_visw(p)

            # Determine correct phase
            if d > goc:
                fluid_type = "gas"
                psat = pdew
                gor = 1.0 / rv
                den = deng

            elif d >= woc:
                fluid_type = "wat"
                psat = pbub
                den = denw
                gor = rs

            else:
                fluid_type = "oil"
                psat = pbub
                den = deno
                gor = rs

            # Set depth node fluid properties
            self.res_depth.append(d)
            self.res_fluid_type.append(fluid_type)
            self.res_pres.append(p)
            self.res_psat.append(psat)
            self.res_pbub.append(pbub)
            self.res_pdew.append(pdew)
            self.res_den.append(den)
            self.res_deng.append(deng)
            self.res_deno.append(deno)
            self.res_denw.append(denw)
            self.res_gor.append(gor)
            self.res_rs.append(rs)
            self.res_rv.append(rv)
            self.res_bo.append(bo)
            self.res_bg.append(bg)
            self.res_bw.append(bw)
            self.res_viso.append(viso)
            self.res_visg.append(visg)
            self.res_visw.append(visw)

            # Update node depth
            d_next = d + delta_d

            if abs(d_next - goc) < delta_d:
                d_next = goc
            if abs(d_next - woc) < delta_d:
                d_next = woc

            # Update new node pressure
            p = p + GD * den * (d_next - d)

            d = d_next

    # -----------------------------------------------------------------------------
    def print_depth_tables(self):
        """
        Print out fluid properties vs depth

        """

        print()
        print("------------------------------------------------------------")
        print("Calculated fluid PVT properties vs. depth")
        print("EQLNUM : %s" % (self.eqlnum))
        print("PVTNUM : %s" % (self.pvt_model.pvtnum))
        print("--------......----------------------------------------------")
        print()

        hdrs = [
            "Depth",
            "Fluid",
            "Pres",
            "Psat",
            "GOR",
            "Den",
            "Pbub",
            "Rs",
            "Deno",
            "Bo",
            "Viso",
            "Pdew",
            "Rv",
            "Deng",
            "Visg",
            "Denw",
            "Bw",
            "Visw",
        ]

        units = [
            "(m)",
            "string",
            "(bar)",
            "(bar)",
            "(sm3/sm3)",
            "(kg/m3)",
            "(bar)",
            "(sm3/sm3)",
            "(kg/m3)",
            "(m3/sm3)",
            "(cp)",
            "(bar)",
            "(sm3/sm3)",
            "(kg/sm3)",
            "(cp)",
            "(kg/m3)",
            "(m3/sm3)",
            "(cp)",
        ]

        fmt = "%-10s " * len(hdrs)
        print(fmt % tuple(hdrs))
        print(fmt % tuple(units))

        vals = tuple(
            zip(
                self.res_depth,
                self.res_fluid_type,
                self.res_pres,
                self.res_psat,
                self.res_gor,
                self.res_den,
                self.res_pbub,
                self.res_rs,
                self.res_deno,
                self.res_bo,
                self.res_viso,
                self.res_pdew,
                self.res_rv,
                self.res_deng,
                self.res_bg,
                self.res_visg,
                self.res_denw,
                self.res_bw,
                self.res_visw,
            )
        )

        fmt = "%-10.3e %-10s " + "%-10.3e " * (len(vals[0]) - 2)

        [print(fmt % v) for v in vals]

        print()

    # -----------------------------------------------------------------------------
    def pvt_gradient_check(self):
        """
        Performs a fluid PVT vs depth table consistency check

        Generates consistent RSVD and RVVD tables
        """
        no_warnings = 0
        no_errors = 0
        no_fatal_errors = 0

        top = self.top_struct
        goc = self.goc
        woc = self.owc

        # tol_depth = 0.1  # Depth tolerance for location of GOC, m
        tol_pres = 0.1  # Pressure difference tolerance, bar
        max_psat_grad = 1.0  # Considered to be very high psat gradient, bar/m

        # Consistency check at GOC
        if top < goc < woc:
            delta = [abs(d - goc) for d in self.res_depth]
            i = delta.index(min(delta))

            # Oil and gas density at GOC
            if self.res_deno[i] <= self.res_deng[i]:

                print("\nERROR - Inconcsistent phase densities at GOC:")
                print("%s : %8.2f" % ("Oil density (kg/m3)", self.res_deno[i]))
                print("%s : %8.2f" % ("Gas density (kg/m3)", self.res_deng[i]))

                no_fatal_errors += 1

            # Psat > press
            if (
                self.res_pbub[i] > self.res_pres[i] + tol_pres
                or self.res_pdew[i] > self.res_pres[i] + tol_pres
            ):

                print("\nERROR - Psat higher than pressure gas-oil-contact:")
                print("%s : %8.2f" % ("Res. pressure (bar)", self.res_pres[i]))
                print("%s : %8.2f" % ("Bubble-point pressure", self.res_pbub[i]))
                print("%s : %8.2f" % ("Dew-point pressure", self.res_pdew[i]))

                no_errors += 1

            # undersaturated GOC
            if (
                self.res_pbub[i] + tol_pres < self.res_pres[i]
                or self.res_pdew[i] + tol_pres < self.res_pres[i]
            ):

                print("\nWARNING - Undersaturated gas-oil-contact:")
                print("%s : %8.2f" % ("Res. pressure (bar)", self.res_pres[i]))
                print("%s : %8.2f" % ("Bubble-point pressure", self.res_pbub[i]))
                print("%s : %8.2f" % ("Dew-point pressure", self.res_pdew[i]))

                no_warnings += 1

        # Check consistency for all depth nodes
        for i in range(1, len(self.res_depth)):

            d_1 = self.res_depth[i - 1]
            d = self.res_depth[i]

            # if abs(d - goc) < tol_depth:
            #    next

            # Psat
            xi_1 = self.res_psat[i - 1]
            xi = self.res_psat[i]
            dxdz = (xi - xi_1) / (d - d_1)

            if d < goc and xi > xi_1:

                print(
                    "ERROR: Non-monotinic dew-points\
                       in depth interval [%6.1d - %6.1d]"
                ) % (d_1, d)

                no_fatal_errors += 1

            if d > goc and xi > xi_1:

                print(
                    "ERROR: Non-monotinic bubble-points\
                       in depth interval [%6.1d - %6.1d]"
                ) % (d_1, d)

                no_fatal_errors += 1

            if xi > self.res_pres[i]:

                print(
                    "ERROR: Sat. pressure %4.2f > res. pressure %4.2f \
                       in depth interval [%6.1d - %6.1d]"
                ) % (abs(dxdz), max_psat_grad, d_1, d)

                no_errors += 1

            if abs(dxdz) > max_psat_grad:

                print(
                    "WARNNING: Bubble-point gradient %4.2f > %4.2f \
                       in depth interval [%6.1d - %6.1d]"
                ) % (abs(dxdz), max_psat_grad, d_1, d)

                no_warnings += 1

        return (no_fatal_errors, no_errors, no_warnings)

    # -----------------------------------------------------------------------------
    def inplace_report(self, no_nodes=20):
        """
        Calculate reservoir height weighted in place,
        as if porevolume is linear with depth

        Can be used to quantify potential effects on in-place when RSVD
        and RVVD tables are changed

        Returns (ggip, ogip, ooip, goip ), where:

            - ggip  : in place surface gas from gas zone
            - ogip  : in place surface oil (condensate) from gas zone
            - ooip  : in-place surface oil from oil zone
            - goip  : in-place solution gas from oil zone

        """

        if no_nodes != 20:
            raise ValueError("no_nodes not implemented")

        ooip = 0.0
        goip = 0.0
        ogip = 0.0
        ggip = 0.0

        for i in range(1, len(self.res_depth)):

            d = self.res_depth[i]
            dh = d - self.res_depth[i - 1]

            bo = self.res_bo[i]
            rs = self.res_rs[i]
            bg = self.res_bg[i]
            rv = self.res_rv[i]

            if d <= self.goc:
                ggip += dh / bg
                ogip += dh * rv / bg

            elif d <= self.owc:
                ooip += dh / bo
                goip += dh * rs / bo

        print()
        print("------------------------------------------------------------")
        print("Reservoir height weighted in place report")
        print("EQLNUM : %s" % (self.eqlnum))
        print("PVTNUM : %s" % (self.pvt_model.pvtnum))
        print("------------------------------------------------------------")
        print()
        print("Surface gas from gas zone: %10.3e" % (ggip))
        print("Surface oil from gas zone: %10.3e" % (ogip))
        print("Surface oil from oil zone: %10.3e" % (ooip))
        print("Surface gas from oil zone: %10.3e" % (goip))
        print()

        return (ggip, ogip, ooip, goip)

    # -----------------------------------------------------------------------------
    def modify_rsvd_rvvd(self, allow_usat_goc=True):
        """
        UNDER CONSTRUCTION!
        Returns consistent RSVD and  RVVD tables

        """

        new_rsvd_depth = []
        new_rsvd_rs = []
        new_rvvd_depth = []
        new_rvvd_rv = []

        top = self.top_struct
        goc = self.goc
        woc = self.owc

        if goc >= woc:

            i_goc = len(self.res_depth) - 1

            new_rvvd_depth.append(self.res_depth[-1])
            new_rvvd_rv.append(self.res_depth[-1])

        elif goc >= top:

            i_goc = 0

            new_rsvd_depth.append(self.res_depth[0])
            new_rvvd_rv.append(self.res_depth[0])

        # Correct tables at GOC
        elif top < goc < woc:

            delta = [abs(d - goc) for d in self.res_depth]
            i_goc = delta.index(min(delta))

            new_rvvd_depth.append(goc)
            new_rsvd_depth.append(goc)

            rv = self.res_rv[i_goc]
            rs = self.res_rs[i_goc]

            # Pbub > press
            if self.res_pbub[i_goc] > self.res_pres[i_goc]:

                print("\nCorrecting pbub higher than pressure gas-oil-contact")

                rs = self.pvt_model.calc_rs(self.res_pres[i_goc])

            # undersaturated psat
            elif not allow_usat_goc and self.res_psat[i_goc] < self.res_pres[i_goc]:

                print("\nCorrecting undersaturated bub-point at GOC")

                rs = self.pvt_model.calc_rs(self.res_pres[i_goc])

            # Pdew > press
            if self.res_pdew[i_goc] > self.res_pres[i_goc]:

                print("\nCorrecting pdew higher than pressure gas-oil-contact")

                rv = self.pvt_model.calc_rv(self.res_pres[i_goc])

            # undersaturated pdew
            elif not allow_usat_goc and self.res_pdew[i_goc] < self.res_pres[i_goc]:

                print("\nCorrecting undersaturated dew-point at GOC")

                rv = self.pvt_model.calc_rv(self.res_pres[i_goc])

            new_rsvd_rs.append(rs)
            new_rvvd_rv.append(rv)

        # For gas RVVD table - traverse upwards from GOC to TOP
        for i in range(i_goc - 1, -1, -1):

            new_rvvd_depth.append(self.res_depth[i])

            rv = self.res_rv[i]

            if rv > new_rvvd_rv[-1]:

                print("\nCorrecting non-monotonic rv")

                rv = new_rvvd_rv[-1]

            if self.res_pdew[i] > self.res_pres[i]:

                print("\nCorrecting psat higher than reservoir pressure")

                rv = self.pvt_model.calc_rv(self.res_pres[i_goc])

            new_rvvd_rv.append(rv)

        new_rvvd_depth.reverse()
        new_rvvd_rv.reverse()

        # Oil RSVD table, correct from GOC and downwards
        for i in range(i_goc + 1, len(self.res_depth)):

            new_rvvd_depth.append(self.res_depth[i])

            rs = self.res_rs[i]

            if rs > new_rsvd_rs[-1]:

                print("\nCorrecting non-monotonic rs")

                rs = new_rsvd_rs[-1]

            if self.res_pbub[i] > self.res_pres[i]:

                print("\nCorrecting psat higher than reservoir pressure")

                rs = self.pvt_model.calc_rs(self.res_pres[i_goc])

            new_rsvd_rs.append(rs)

        return (new_rsvd_depth, new_rsvd_rs, new_rvvd_depth, new_rvvd_rv)

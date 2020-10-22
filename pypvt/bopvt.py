""" Black-oil PVT module """

import numpy as np

from scipy.interpolate import interp1d

# pylint: disable=invalid-name
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements

# =============================================================================


class BoPVT:
    """
    Black oil pvt fluid model for a given fluid PVT region

    Contains standard black-oil tables and methods for calculation of standard
    fluid properties based on the PVT tables

    NB: The PVT-table routines do not allow extrapolation -
    This should potentially be revised

    """

    PRINT_WARNING = False  # Prints warnings input is outside PVT table range

    # -|-----------------------------------------------------------------------
    def __init__(
        self,
        pvtnum=None,
        sdeno=None,
        pvto_arr=None,
        sdeng=None,
        pvtg_arr=None,
        sdenw=None,
        pvtw_arr=None,
        pvt_logger=None,
    ):

        self.pvtnum = pvtnum

        # Surface oil, gas and water densities (Kg/Sm3)
        self.sdeno = sdeno
        self.sdeng = sdeng
        self.sdenw = sdenw

        # E100-PVT tables (2D numpy arrays)
        self.pvto = pvto_arr  # PVTO table containing RS, pres, Bo and Viso )
        self.pvtg = pvtg_arr  # PVTG table containing pres, rv, Bg and Visg )
        self.pvtw = pvtw_arr  # PVTW table containing pref, Bwref, Cw visw_ref and Cv

        self.pvt_logger = pvt_logger
        self.calc_rs_warning = False
        self.calc_pbub_warning = False

    # ------------------------------------------------------------------------
    def set_PRINT_WARNING(self, print_warning=True):

        """
        Set PRINT WARNING option

        """
        self.PRINT_WARNING = print_warning

    # ------------------------------------------------------------------------
    def set_pvtnum(self, pvtnum):

        """
        Set pvtnum
        """
        self.pvtnum = pvtnum

    # ------------------------------------------------------------------------
    def set_densities_from_df(self, eql_df):

        """
        Set surface densities from an ecl2df.density_df object
        """

        if self.pvtnum is None:
            raise ValueError("ERROR: PVTNUM not set")

        if self.pvtnum not in eql_df.PVTNUM.unique():
            raise ValueError("PVTNUM not found in DENSITY dataframe")

        self.sdeno = eql_df[eql_df["PVTNUM"] == self.pvtnum]["OILDENSITY"].unique()[0]
        self.sdeng = eql_df[eql_df["PVTNUM"] == self.pvtnum]["GASDENSITY"].unique()[0]
        self.sdenw = eql_df[eql_df["PVTNUM"] == self.pvtnum]["WATERDENSITY"].unique()[0]

    # ------------------------------------------------------------------------
    def set_pvtg_from_df(self, eql_df):

        """
        Set PVTG array from an ecl2df.PVTO_df object
        """

        if self.pvtnum is None:
            raise ValueError("ERROR: PVTNUM not set")

        if self.pvtnum not in eql_df.PVTNUM.unique():
            raise ValueError("PVTNUM not found in PVTG dataframe " + str(self.pvtnum))

        required_cols = ["PRESSURE", "OGR", "VOLUMEFACTOR", "VISCOSITY"]
        try:
            df = eql_df[eql_df["PVTNUM"] == self.pvtnum][required_cols]
        except ValueError:
            print("Required dataframe columns headers are: " + str(required_cols))

        self.pvtg = df.to_numpy()

    # ------------------------------------------------------------------------
    def set_pvto_from_df(self, eql_df):

        """
        Set PVTO array from an ecl2df.PVTO_df object
        """

        if self.pvtnum is None:
            raise ValueError("ERROR: PVTNUM not set")

        if self.pvtnum not in eql_df.PVTNUM.unique():
            raise ValueError("PVTNUM not found in PVTO dataframe")

        required_cols = ["RS", "PRESSURE", "VOLUMEFACTOR", "VISCOSITY"]
        try:
            df = eql_df[eql_df["PVTNUM"] == self.pvtnum][required_cols]
        except ValueError:
            print("Required dataframe columns headers are: " + str(required_cols))

        self.pvto = df.to_numpy()

    # ------------------------------------------------------------------------
    def set_pvtw_from_df(self, eql_df):

        """
        Set PVTW array from an ecl2df.PVTW_df object
        """

        if self.pvtnum is None:
            raise ValueError("ERROR: PVTNUM not set")

        if self.pvtnum not in eql_df.PVTNUM.unique():
            raise ValueError("PVTNUM not found in PVTW dataframe")

        required_cols = [
            "PRESSURE",
            "VOLUMEFACTOR",
            "COMPRESSIBILITY",
            "VISCOSITY",
            "VISCOSIBILITY",
        ]
        try:
            df = eql_df[eql_df["PVTNUM"] == self.pvtnum][required_cols]
        except ValueError:
            print("Required dataframe columns headers are: " + str(required_cols))

        self.pvtw = df.to_numpy()

    # ------------------------------------------------------------------------
    def check_pvt_input(self):
        """
        Under construction for now!

        Check that all required PVT input is given and checks PVT model consistencies

        ...Ideally the consistency check should include full PVT table checks,
        such as negative compressibility checks, crossing saturated values, montonocities etc. etc.

        """

        raise NotImplementedError

    # -------------------------------------------------------------------------
    def calc_rs(self, pbub):
        """
        Returns Rs (solution gas-oil-ratio) for given bubble-point pressure

        Based on linear interpolation in PVTO table.

        NB: Does not allow extrapolation outside table ranges

        """
        pvto = self.pvto

        rs_tab = np.unique(pvto[:, 0], axis=0)

        pb_tab = []
        for rs in rs_tab:
            pressures = [r[1] for r in pvto if r[0] == rs]
            pb_tab.append(pressures[0])

        if pbub > max(pb_tab) or pbub < min(pb_tab):

            msg = "{} of {:6.1f} outside PVT table interval [{:6.1f} , {:6.1f}]".format(
                "Pbub", pbub, min(pb_tab), max(pb_tab)
            )
            if not self.calc_rs_warning:
                self.pvt_logger.warning(msg, extra={"pvtnum": self.pvtnum})
                self.calc_rs_warning = True
                print("\nERROR:", msg)
            raise ValueError("Pbub outside PVTO table interval")

        rs = np.interp(pbub, pb_tab, rs_tab)

        return rs

    # -------------------------------------------------------------------------
    def calc_pbub(self, rs):
        """
        Returns bubble-point for given solution oil-gas-ratio

        Based on linear interpolation in PVTO table.

        NB: Does not allow extrapolation outside PVTO range

        """
        pvto = self.pvto

        rs_tab = np.unique(pvto[:, 0], axis=0)

        pb_tab = []
        for rst in rs_tab:
            pressures = [r[1] for r in pvto if r[0] == rst]
            pb_tab.append(pressures[0])

        if rs > max(rs_tab) or rs < min(rs_tab):

            msg = "{} of {:6.2f} outside PVT table interval [{:6.2f} , {:6.2f}]".format(
                "RS", rs, min(rs_tab), max(rs_tab)
            )

            if not self.calc_pbub_warning:
                self.pvt_logger.warning(msg, extra={"pvtnum": self.pvtnum})
                self.calc_pbub_warning = True
                print("\nWARNING:", msg)

            # raise ValueError("RS outside PVTO table range")

        pbub = np.interp(rs, rs_tab, pb_tab)

        return pbub

    # -------------------------------------------------------------------------
    def calc_bo(self, pres, **kwargs):
        """
        Returns Bo for given pressure (and optionally rs OR pbub)

        If only pressure is given, the saturated Bo is returned

        NB: Does not allow extrapolation outside PVTO table range
        """

        if len(kwargs) > 1:
            raise ValueError("Too many arguments in function call to calc_bo")

        pvto = self.pvto

        # ---------------------------------------------------------------------
        # Return saturated BO
        # ---------------------------------------------------------------------
        if len(kwargs) == 0:

            rs_tab = np.unique(pvto[:, 0], axis=0)

            pb_tab = []
            sat_bo_tab = []

            for rst in rs_tab:
                pressures = [r[1] for r in pvto if r[0] == rst]
                pb_tab.append(pressures[0])

                bos = [r[2] for r in pvto if r[0] == rst]
                sat_bo_tab.append(bos[0])

            if pres < min(pb_tab) or pres > max(pb_tab):
                raise ValueError("Saturation pressure outside PVTO table range")

            bo = np.interp(pres, pb_tab, sat_bo_tab)

        # ---------------------------------------------------------------------
        # Return undersaturated BO
        # ---------------------------------------------------------------------
        else:

            arg_name = list(kwargs.keys())[0]

            if arg_name == "rs":
                rs = kwargs[arg_name]
                pbub = self.calc_pbub(rs)

                if pbub > pres:
                    print("RS = ", rs, "PBUB =", pbub)
                    raise ValueError("Rs gives pbub higher than reservoir pressure")

            elif arg_name == "pbub":
                pbub = kwargs[arg_name]

                if pbub > pres:
                    raise ValueError("Bubble-point higher than reservoir pressure")

                rs = self.calc_rs(pbub)

            else:
                raise ValueError("Unrecognized argument " + arg_name)

            # NOTE: If speed is an issue - the following interpolation
            # should be done smarter

            rs_tab = np.unique(pvto[:, 0], axis=0)

            bo_tab = []

            # Interpolate for all undersaturated pressures entries
            for rst in rs_tab:
                pressures = [r[1] for r in pvto if r[0] == rst]
                bos = [r[2] for r in pvto if r[0] == rst]

                bo = np.interp(pres, pressures, bos)
                bo_tab.append(bo)

            bo = np.interp(rs, rs_tab, bo_tab)

        return bo

    # -------------------------------------------------------------------------
    def calc_viso(self, pres, **kwargs):
        """
        Returns Viso for given pressure (and optionally rs OR pbub)

        If only pressure is given, the saturated Viso is returned

        NB: Uses constant extraplation outside table ranges - This should
        be updated
        """

        if len(kwargs) > 1:
            raise ValueError("Too many arguments in function call to calc_bo")

        pvto = self.pvto

        # ---------------------------------------------------------------------
        # Return saturated viso
        # ---------------------------------------------------------------------
        if len(kwargs) == 0:

            rs_tab = np.unique(pvto[:, 0], axis=0)

            pb_tab = []
            sat_viso_tab = []

            for rst in rs_tab:
                pressures = [r[1] for r in pvto if r[0] == rst]
                pb_tab.append(pressures[0])

                visos = [r[3] for r in pvto if r[0] == rst]
                sat_viso_tab.append(visos[0])

            if pres < min(pb_tab) or pres > max(pb_tab):
                raise ValueError("Saturation pressure outside PVTO table range")

            viso = np.interp(pres, pb_tab, sat_viso_tab)

        # ---------------------------------------------------------------------
        # Return undersaturated viso
        # ---------------------------------------------------------------------
        else:

            arg_name = list(kwargs.keys())[0]

            if arg_name == "rs":
                rs = kwargs[arg_name]
                pbub = self.calc_pbub(rs)

                if pbub > pres:
                    print("RS = ", rs, "PBUB =", pbub)
                    raise ValueError("Rs gives pbub higher than reservoir pressure")

            elif arg_name == "pbub":
                pbub = kwargs[arg_name]

                if pbub > pres:
                    raise ValueError("Bubble-point higher than reservoir pressure")

                rs = self.calc_rs(pbub)

            else:
                raise ValueError("Unrecognized argument " + arg_name)

            # NOTE: If speed is an issue - the following interpolation
            # should be done smarter

            rs_tab = np.unique(pvto[:, 0], axis=0)

            viso_tab = []

            # Interpolate for all undersaturated pressures entries
            for rst in rs_tab:
                pressures = [r[1] for r in pvto if r[0] == rst]
                visos = [r[3] for r in pvto if r[0] == rst]

                viso = np.interp(pres, pressures, visos)
                viso_tab.append(viso)

            viso = np.interp(rs, rs_tab, viso_tab)

        return viso

    # -------------------------------------------------------------------------
    def calc_deno(self, pres, **kwargs):
        """
        Returns reservoir oil density for given pressure (and optionally rs OR pbub)

        If only pressure is given, the saturated density is returned

        """

        # Calculate rs
        if len(kwargs) == 0:

            rs = self.calc_rs(pres)

        else:

            arg_name = list(kwargs.keys())[0]

            if arg_name == "rs":

                rs = kwargs[arg_name]

            elif arg_name == "pbub":

                pbub = kwargs[arg_name]
                rs = self.calc_rs(pbub)

            else:
                raise ValueError("Unrecognized argument " + arg_name)

        bo = self.calc_bo(pres, **kwargs)

        deno = (self.sdeno + rs * self.sdeng) / bo

        return deno

    # -------------------------------------------------------------------------
    def calc_rv(self, pdew):
        """
        Returns rv (solution oil-gas-ratio) for given dew-point pressure

        Based on linear interpolation in PVTG table.

        NB: Does not allow for extrapolation outside PVTG table range

        """

        pvtg = self.pvtg

        pd_tab = []
        rv_tab = []

        p_prev = -1.0
        for row in pvtg:
            p = row[0]
            rvx = row[1]
            if p != p_prev and rvx not in rv_tab:
                pd_tab.append(p)
                rv_tab.append(rvx)

            p_prev = p

        if pdew > max(pd_tab) or pdew < min(pd_tab):

            # print(
            #    "\nWARNING: %s of %10.3e outside PVT table interval [%10.3e , %10.3e]"
            #    % ("Pdew", pdew, min(pd_tab), max(pd_tab))
            # )
            raise ValueError("Pdew outside PVTG table range")

        rv = np.interp(pdew, pd_tab, rv_tab)

        return rv

    # -------------------------------------------------------------------------
    def calc_pdew(self, rv):
        """
        Returns pdew for given solution oil-gas ratio

        Based on linear interpolation in PVTG table.

        NB: Does not allow for extrapolation outside PVTG table range

        """

        pvtg = self.pvtg

        pd_tab = []
        rv_tab = []

        p_prev = -1.0
        for row in pvtg:
            p = row[0]
            rvx = row[1]
            if p != p_prev and rvx not in rv_tab:
                pd_tab.append(p)
                rv_tab.append(rvx)

            p_prev = p

        if rv > max(rv_tab) or rv < min(rv_tab):

            # print(
            #    "\nWARNING: %s of %10.3e outside PVT table interval [%10.3e , %10.3e]"
            #    % ("Rv", rv, min(rv_tab), max(rv_tab))
            # )

            print("UNCOMMENT?")
            if rv > max(rv_tab):
                rv = max(rv_tab)
            if rv < min(rv_tab):
                rv = min(rv_tab)

            # raise ValueError("Rv outside PVTG table range")

        f = interp1d(rv_tab, pd_tab)
        pdew = f(rv)

        return pdew

    # -------------------------------------------------------------------------
    def calc_bg(self, pres, **kwargs):
        """
        Returns Bg for given pressure (and optionally rv OR pdew)

        If only pressure is given, the saturated Bg is returned

        NB: Does not allow for extrapolation

        """

        if len(kwargs) > 1:
            raise ValueError("Too many arguments in function call to calc_bg")

        pvtg = self.pvtg

        # ---------------------------------------------------------------------
        # Return saturated Bg (note E100 interpolates 1/Bg)
        # ---------------------------------------------------------------------
        if len(kwargs) == 0:

            pd_tab = []
            rv_tab = []
            inv_bg_tab = []

            p_prev = -1.0
            for row in pvtg:
                p = row[0]
                rvx = row[1]
                bg = row[2]
                if p != p_prev and rvx not in rv_tab:
                    pd_tab.append(p)
                    rv_tab.append(rvx)
                    inv_bg_tab.append(1.0 / bg)

                p_prev = p

            if pres > max(pd_tab) or pres < min(pd_tab):
                raise ValueError("Pdew outside PVTG table range")

            inv_bg = np.interp(pres, pd_tab, inv_bg_tab)
            bg = 1.0 / inv_bg

        # ---------------------------------------------------------------------
        # Return undersaturated Bg
        # ---------------------------------------------------------------------
        else:

            arg_name = list(kwargs.keys())[0]

            if arg_name == "rv":
                rv = kwargs[arg_name]
                pdew = self.calc_pdew(rv)

                if pdew > pres:
                    print("Rv = ", rv, "PDEW =", pdew)
                    raise ValueError("Rv gives pdew higher than reservoir pressure")

            elif arg_name == "pdew":
                pdew = kwargs[arg_name]

                if pdew > pres:
                    raise ValueError("Dew-point higher than reservoir pressure")

                rv = self.calc_rv(pdew)

            else:
                raise ValueError("Unrecognized argument " + arg_name)

            # NOTE: If speed is an issue - the following interpolation
            # should be done smarter

            p_tab = np.unique(pvtg[:, 0], axis=0)  # include all pressure entries

            inv_bg_tab = []

            # Interpolate for all rv
            for p in p_tab:
                rvt = [
                    r[1] for r in pvtg if r[0] == p
                ]  # pick up all rvs for given pressure
                inv_bgt = [1.0 / r[2] for r in pvtg if r[0] == p]

                if len(rvt) <= 1:
                    inv_bg = inv_bgt[0]

                else:
                    f = interp1d(rvt, inv_bgt)
                    x = max(min(rvt), rv)
                    x = min(max(rvt), x)
                    inv_bg = f(x)

                inv_bg_tab.append(inv_bg)

            inv_bg = np.interp(pres, p_tab, inv_bg_tab)
            bg = 1.0 / inv_bg

        return bg

    # -------------------------------------------------------------------------
    def calc_deng(self, pres, **kwargs):
        """
        Returns reservoir gas density for given pressure (and optionally rv OR pdew)

        If only pressure is given, the saturated density is returned
        """

        # Calculate rv
        if len(kwargs) == 0:

            rv = self.calc_rv(pres)

        else:

            arg_name = list(kwargs.keys())[0]

            if arg_name == "rv":

                rv = kwargs[arg_name]

            elif arg_name == "pdew":

                pdew = kwargs[arg_name]
                rv = self.calc_rv(pdew)

            else:
                raise ValueError("Unrecognized argument " + arg_name)

        bg = self.calc_bg(pres, **kwargs)

        deng = (self.sdeng + rv * self.sdeno) / bg

        return deng

    # -------------------------------------------------------------------------
    def calc_visg(self, pres, **kwargs):
        """

        Returns reservoir gas viscosity for given pressure (and optionally rv OR pdew)

        If only pressure is given, the saturated viscosity is returned

        Note: E100 Interpolates as 1/(Bg*visg)
        """

        if len(kwargs) > 1:
            raise ValueError("Too many arguments in function call to calc_visg")

        pvtg = self.pvtg

        # ---------------------------------------------------------------------
        # Return saturated Visg (note E100 interpolates 1/(Bg*Visg)
        # ---------------------------------------------------------------------
        if len(kwargs) == 0:

            pd_tab = []
            rv_tab = []
            inv_bv_tab = []

            p_prev = -1.0
            for row in pvtg:
                p = row[0]
                rvx = row[1]
                b = row[2]
                v = row[3]
                if p != p_prev and rvx not in rv_tab:
                    pd_tab.append(p)
                    rv_tab.append(rvx)
                    inv_bv_tab.append(1.0 / (b * v))

                p_prev = p

            if pres > max(pd_tab) or pres < min(pd_tab):
                raise ValueError("Pdew outside PVTG table range")

            inv_bv = np.interp(pres, pd_tab, inv_bv_tab)

            bg = self.calc_bg(pres, **kwargs)

            visg = 1.0 / (inv_bv * bg)

        # ---------------------------------------------------------------------
        # Return undersaturated Visg
        # ---------------------------------------------------------------------
        else:

            arg_name = list(kwargs.keys())[0]

            if arg_name == "rv":
                rv = kwargs[arg_name]
                pdew = self.calc_pdew(rv)

                if pdew > pres:
                    print("Rv = ", rv, "PDEW =", pdew)
                    raise ValueError("Rv gives pdew higher than reservoir pressure")

            elif arg_name == "pdew":
                pdew = kwargs[arg_name]

                if pdew > pres:
                    raise ValueError("Dew-point higher than reservoir pressure")

                rv = self.calc_rv(pdew)

            else:
                raise ValueError("Unrecognized argument " + arg_name)

            # NOTE: If speed is an issue - the following interpolation
            # should be done smarter

            pd_tab = np.unique(pvtg[:, 0], axis=0)

            inv_bv_tab = []

            # Interpolate for rv, all pressures
            for p in pd_tab:
                rvt = [r[1] for r in pvtg if r[0] == p]
                inv_bvt = [1.0 / (r[2] * r[3]) for r in pvtg if r[0] == p]

                if len(rvt) <= 1:
                    inv_bv = inv_bvt[0]

                else:
                    f = interp1d(rvt, inv_bvt)
                    x = max(min(rvt), rv)
                    x = min(max(rvt), x)
                    inv_bv = f(x)

                inv_bv_tab.append(inv_bv)

            inv_bv = np.interp(pres, pd_tab, inv_bv_tab)

            bg = self.calc_bg(pres, **kwargs)

            visg = 1.0 / (inv_bv * bg)

        return visg

    # -------------------------------------------------------------------------
    def calc_bw(self, pres):
        """

        Returns reservoir water Bw for given pressure

        Uses E100 method for calculating Bw
        """

        p_ref = self.pvtw[0, 0]
        bw_ref = self.pvtw[0, 1]
        cw = self.pvtw[0, 2]

        x = cw * (pres - p_ref)

        bw = bw_ref / (1.0 + x + (x * x / 2.0))

        return bw

    # -------------------------------------------------------------------------
    def calc_denw(self, pres):
        """

        Returns reservoir water density for given pressure

        Uses E100 method for calculating Bw
        """

        bw = self.calc_bw(pres)

        denw = self.sdenw / bw

        return denw

    # -------------------------------------------------------------------------
    def calc_visw(self, pres):
        """

        Returns reservoir water viscosity for given pressure

        Uses E100 method for calculating visw (check PVTW keyword in ECL manual)
        """

        p_ref = self.pvtw[0, 0]
        bw_ref = self.pvtw[0, 1]
        cw = self.pvtw[0, 2]
        visw_ref = self.pvtw[0, 3]
        cv = self.pvtw[0, 4]

        y = (cw - cv) * (pres - p_ref)

        bw_visw = bw_ref * visw_ref / (1.0 + y + (y * y / 2.0))

        bw = self.calc_bw(pres)

        visw = bw_visw / bw

        return visw

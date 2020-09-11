""" Black-oil PVT module """


import numpy as np

from scipy.interpolate import interp1d

# pylint: disable=invalid-name
# pylint: disable=too-many-arguments
# pylint: disable=no-else-return
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=raise-missing-from

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

    # ------------------------------------------------------------------------
    def __init__(
        self,
        pvtnum=None,
        sdeno=None,
        pvto_arr=None,
        sdeng=None,
        pvtg_arr=None,
        sdenw=None,
        pvtw_arr=None,
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
        except:
            raise ValueError(
                "Required dataframe columns headers are: " + str(required_cols)
            )

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
        except:
            raise ValueError(
                "Required dataframe columns headers are: " + str(required_cols)
            )

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
        except:
            raise ValueError(
                "Required dataframe columns headers are: " + str(required_cols)
            )

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

            # print(
            #    "\nWARNING: %s of %10.3e outside PVT table interval [%10.3e , %10.3e]"
            #    % ("Pbub", pbub, min(pb_tab), max(pb_tab))
            # )
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

            # print(
            #    "\nWARNING: %s of %10.3e outside PVT table interval [%10.3e , %10.3e]"
            #    % ("RS", rs, min(rs_tab), max(rs_tab))
            # )
            raise ValueError("RS outside PVTO table range")

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

            return bo

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

            return viso

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
        Under construction - Need to solve undersaturated entries

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
        Under construction - Need to solve undersaturated table entries

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
            raise ValueError("Rv outside PVTG table range")

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

            return bg

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

                if len(rvt) < 1:
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

            return visg

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

            pd_tab = np.unique(pvtg[:, 0], axis=0)

            inv_bv_tab = []

            # Interpolate for rv, all pressures
            for p in pd_tab:
                rvt = [r[1] for r in pvtg if r[0] == p]
                inv_bvt = [1.0 / (r[2] * r[3]) for r in pvtg if r[0] == p]

                if len(rvt) < 1:
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


## =============================================================================
# def main():
#    df_pvto = pd.read_excel("PVT.xlsx", sheet_name="PVTO", index_col=None)
#
#    df_density = pd.read_excel("PVT.xlsx", sheet_name="DENSITY", index_col=None)
#
#    df_pvtg = pd.read_excel("PVT.xlsx", sheet_name="PVTG", index_col=None)
#
#    df_pvtw = pd.read_excel("PVT.xlsx", sheet_name="PVTW", index_col=None)
#
#    pvtnum = 1
#    pvtmod = BoPVT(pvtnum)
#
#    pvtmod.set_pvto_from_df(df_pvto)
#    pvtmod.set_pvtg_from_df(df_pvtg)
#    pvtmod.set_densities_from_df(df_density)
#    pvtmod.set_pvtw_from_df(df_pvtw)
#
#    pbub = pvtmod.calc_pbub(182)
#    print("PBUB = ", pbub)
#
#    bo = pvtmod.calc_bo(300, rs=182)
#    print("BO = ", bo)
#
#    deno = pvtmod.calc_deno(300, rs=182)
#    print("Deno = ", deno)
#
#    rv = pvtmod.calc_rv(210)
#    print("Rv =", rv)
#
#    pdew = pvtmod.calc_pdew(0.00027601)
#    print("Pdew =", pdew)
#
#    pdew = pvtmod.calc_pdew(1.0)
#    print("Pdew =", pdew)
#
#    bg = pvtmod.calc_bg(200, pdew=125)
#    print("Bg =", bg)
#
#    deng = pvtmod.calc_deng(500)
#    print("Deng =", deng)
#
#    bw = pvtmod.calc_bw(200)
#    print("Bw 200 =", bw)
#
#    bw = pvtmod.calc_bw(400)
#    print("Bw 400 =", bw)
#
#    denw = pvtmod.calc_denw(100)
#    print("Denw =", denw)
#
#    denw = pvtmod.calc_denw(400)
#    print("Denw =", denw)
#
#    visw = pvtmod.calc_visw(600)
#    print("Visw =", visw)
#
#    visg = pvtmod.calc_visg(500)
#    print("Visg =", visg)
#
#    # Initi
#
#    rvvd_depth = [3675.0, 3815.0, 4025.0, 4083.3, 4200.0, 4500.0]
#
#    rvvd_rv = [5.7182e-04, 7.1485e-04, 9.2321e-04, 1.1350e-03, 1.1350e-03, 1.1350e-03]
#
#    rsvd_depth = [3675.0, 3815.0, 4025.0, 4083.3, 4200.0, 4500.0]
#
#    rsvd_rs = [300, 290, 202, 203, 200, 200]
#
#    fluid_model = FluidModel(
#        eqlnum=1,
#        top_grid=3600,
#        bottom_grid=4500,
#        woc=4400,
#        goc=4000,
#        ref_press=466,
#        ref_depth=3950,
#        rsvd_depth=rsvd_depth,
#        rsvd_rs=rsvd_rs,
#        rvvd_depth=rvvd_depth,
#        rvvd_rv=rvvd_rv,
#        pvt_model=pvtmod,
#    )
#
#    fluid_model.calc_fluid_prop_vs_depth(no_nodes=20)
#    fluid_model.print_depth_tables()
#
#
# if __name__ == "__main__":
#    main()

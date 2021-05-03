"""Test bopvt"""

import pathlib

import numpy as np
import ecl2df

from pypvt.bopvt import BoPVT

# pylint: disable=invalid-name
# pylint: disable=too-many-arguments
# pylint: disable=no-else-return
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=raise-missing-from

# from pypvt import BoPVT

TESTDATA = pathlib.Path(__file__).resolve().parent / "data"


def test_main():
    pass


def init_from_ecl_df():
    """Reads pvt data and returns list of bopvt objects"""

    pvt_txt = (TESTDATA / "pvt").read_text(encoding="utf-8", errors="ignore")
    pvt_df = ecl2df.pvt.df(pvt_txt)

    bopvt_models = []

    for pvtnr in pvt_df["PVTNUM"].unique():

        print("Initialising pvtmodel ", pvtnr)
        pvt_model = BoPVT()

        pvt_model.set_pvtnum(pvtnr)

        df = pvt_df[(pvt_df["KEYWORD"] == "PVTO") & (pvt_df["PVTNUM"] == pvtnr)][
            ["RS", "PRESSURE", "VOLUMEFACTOR", "VISCOSITY", "PVTNUM"]
        ]
        pvt_model.set_pvto_from_df(df)

        df = pvt_df[(pvt_df["KEYWORD"] == "PVTG") & (pvt_df["PVTNUM"] == pvtnr)][
            ["PRESSURE", "OGR", "VOLUMEFACTOR", "VISCOSITY", "PVTNUM"]
        ]
        pvt_model.set_pvtg_from_df(df)

        df = pvt_df[(pvt_df["KEYWORD"] == "PVTW") & (pvt_df["PVTNUM"] == pvtnr)][
            [
                "PRESSURE",
                "VOLUMEFACTOR",
                "COMPRESSIBILITY",
                "VISCOSITY",
                "VISCOSIBILITY",
                "PVTNUM",
            ]
        ]
        pvt_model.set_pvtw_from_df(df)

        df = pvt_df[(pvt_df["KEYWORD"] == "DENSITY") & (pvt_df["PVTNUM"] == pvtnr)][
            ["OILDENSITY", "GASDENSITY", "WATERDENSITY", "PVTNUM"]
        ]
        pvt_model.set_densities_from_df(df)

        bopvt_models.append(pvt_model)

    return bopvt_models


def test_pvto():
    """Test BoPVT oil properties calculations"""

    pvt_models = init_from_ecl_df()

    pvtnum = 1
    pvt_model = pvt_models[pvtnum - 1]

    # Calculation of rs
    p = 200
    rs = np.interp(p, [148.9, 213.3], [71.28, 102.664])
    assert np.isclose(pvt_model.calc_rs(p), rs)

    # Calculation of pbub
    rs = 230
    pbub = np.interp(rs, [220.383, 273.671], [406.7, 471.1])
    assert np.isclose(pvt_model.calc_pbub(rs), pbub)

    pvtnum = 2
    pvt_model = pvt_models[pvtnum - 1]
    # try:
    #    pvt_model.calc_pbub(rs)
    #    raise ValueError("This should have been outside range")
    # except:
    #    pass

    bo = np.interp(p, [148.9, 213.3], [1.22937, 1.30507])
    assert np.isclose(pvt_model.calc_bo(p), bo)

    p = 500
    pbub = 350
    x1 = [342.2, 392.5, 406.7, 471.1, 535.6, 600.0]
    y1 = [1.47418, 1.46085, 1.45738, 1.44285, 1.43012, 1.41885]
    bo1 = np.interp(p, x1, y1)
    x2 = [392.5, 406.7, 471.1, 535.6, 600.0]
    y2 = [1.55249, 1.54824, 1.53057, 1.51519, 1.50165]
    bo2 = np.interp(p, x2, y2)
    bo = np.interp(pbub, [342.2, 392.5], [bo1, bo2])
    assert np.isclose(pvt_model.calc_bo(p, pbub=pbub), bo)

    rs = pvt_model.calc_rs(pbub)
    assert np.isclose(pvt_model.calc_bo(p, rs=rs), bo)

    deno = (pvt_model.sdeno + rs * pvt_model.sdeng) / bo
    assert np.isclose(pvt_model.calc_deno(p, pbub=pbub), deno)


def test_pvtg():
    """Test BoPVT gas properties calculations"""

    pvt_models = init_from_ecl_df()

    pvtnum = 1
    pvt_model = pvt_models[pvtnum - 1]

    # Calculation of rv
    p = 200
    rv = np.interp(p, [148.9, 213.3], [0.0000318405, 0.0000908863])
    assert np.isclose(pvt_model.calc_rv(p), rv)

    # Calculation of pdew
    assert np.isclose(pvt_model.calc_pdew(rv), p)

    pvtnum = 2
    pvt_model = pvt_models[pvtnum - 1]
    # p = 500.0
    # print (pvt_model.calc_rv(p))

    # Calculate saturated Bg
    p = 500
    inv_bg = np.interp(p, [483.9, 535.6], [1.0 / 0.003296, 1.0 / 0.003187])
    bg = 1.0 / inv_bg
    assert np.isclose(pvt_model.calc_bg(p), bg)

    # Undersaturated Bg
    p = 500
    rv = pvt_model.calc_rv(250)  # 0.00014365481178294572
    inv_bg1 = np.interp(
        rv, [0.0000908863, 0.0001836266], [1.0 / 0.003116, 1.0 / 0.003173]
    )
    inv_bg2 = np.interp(
        rv, [0.0000908863, 0.0001836266], [1.0 / 0.002980, 1.0 / 0.003044]
    )
    inv_bg = np.interp(p, [483.9, 535.6], [inv_bg1, inv_bg2])
    bg = 1.0 / inv_bg
    assert np.isclose(pvt_model.calc_bg(p, rv=rv), bg)
    assert np.isclose(pvt_model.calc_bg(p, pdew=250), bg)

    # Reservoir density
    sdeng = 0.94736
    sdeno = 893.1
    deng = (sdeng + rv * sdeno) / bg
    assert np.isclose(pvt_model.calc_deng(p, rv=rv), deng)

    # Saturated viscosity
    p = 500
    inv_bg = np.interp(p, [483.9, 535.6], [1.0 / 0.003296, 1.0 / 0.003187])
    bg = 1.0 / inv_bg
    inv_bv = np.interp(
        p, [483.9, 535.6], [1.0 / (0.003296 * 0.054124), 1.0 / (0.003187 * 0.059210)]
    )
    visg = 1.0 / (inv_bv * bg)
    assert np.isclose(pvt_model.calc_visg(p), visg)

    # Undersaturated viscosity
    p = 500
    rv = pvt_model.calc_rv(250)  # 0.00014365481178294572
    inv_bg1 = np.interp(
        rv, [0.0000908863, 0.0001836266], [1.0 / 0.003116, 1.0 / 0.003173]
    )
    inv_bg2 = np.interp(
        rv, [0.0000908863, 0.0001836266], [1.0 / 0.002980, 1.0 / 0.003044]
    )
    inv_bg = np.interp(p, [483.9, 535.6], [inv_bg1, inv_bg2])
    bg = 1.0 / inv_bg

    inv_bv1 = np.interp(
        rv,
        [0.0000908863, 0.0001836266],
        [1.0 / (0.003116 * 0.041821), 1.0 / (0.003173 * 0.045360)],
    )
    inv_bv2 = np.interp(
        rv,
        [0.0000908863, 0.0001836266],
        [1.0 / (0.002980 * 0.044733), 1.0 / (0.003044 * 0.048622)],
    )
    inv_bv = np.interp(p, [483.9, 535.6], [inv_bv1, inv_bv2])
    visg = 1.0 / (inv_bv * bg)

    assert np.isclose(pvt_model.calc_visg(p, rv=rv), visg)
    assert np.isclose(pvt_model.calc_visg(p, pdew=250), visg)


def test_pvtw():
    """Test BoPVT water properties calculations"""

    pvt_models = init_from_ecl_df()

    pvtnum = 1
    pvt_model = pvt_models[pvtnum - 1]

    # bw
    p = 400.0
    sdenw = 999.1
    p_ref = 392.5
    bw_ref = 1.01712
    cw = 0.42190e-4
    x = cw * (p - p_ref)
    bw = bw_ref / (1 + x + 0.5 * x ** 2)
    assert np.isclose(pvt_model.calc_bw(p), bw)

    # Water density
    denw = sdenw / bw
    assert np.isclose(pvt_model.calc_denw(p), denw)


if __name__ == "__main__":

    test_pvto()
    test_pvtg()
    test_pvtw()

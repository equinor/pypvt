"""Test element_fluid_description"""

import os
import sys
import numpy as np
import pandas as pd
import ecl2df

from pypvt import ElementFluidDescription

TESTDATA = os.path.join(os.path.dirname(__file__), "data")


def test_main():
    pass


def test_init_from_ecl_df():
    txt = open(
        os.path.join(TESTDATA, "DATA"), "r", encoding="utf-8", errors="ignore"
    ).read()
    txt += open(
        os.path.join(TESTDATA, "equil"), "r", encoding="utf-8", errors="ignore"
    ).read()
    equil_df = ecl2df.equil.df(txt, keywords="EQUIL")

    txt = open(
        os.path.join(TESTDATA, "DATA"), "r", encoding="utf-8", errors="ignore"
    ).read()
    txt += open(
        os.path.join(TESTDATA, "rsvd"), "r", encoding="utf-8", errors="ignore"
    ).read()
    rsvd_df = ecl2df.equil.df(txt, keywords="RSVD")

    txt = open(
        os.path.join(TESTDATA, "DATA"), "r", encoding="utf-8", errors="ignore"
    ).read()
    txt += open(
        os.path.join(TESTDATA, "rvvd"), "r", encoding="utf-8", errors="ignore"
    ).read()
    rvvd_df = ecl2df.equil.df(txt, keywords="RVVD")

    txt = open(
        os.path.join(TESTDATA, "DATA"), "r", encoding="utf-8", errors="ignore"
    ).read()
    txt += open(
        os.path.join(TESTDATA, "pvt"), "r", encoding="utf-8", errors="ignore"
    ).read()
    pvt_df = ecl2df.pvt.df(txt)

    description = ElementFluidDescription(1, 1)
    description.init_from_ecl_df(
        {"EQUIL": equil_df, "RSVD": rsvd_df, "RVVD": rvvd_df, "PVT": pvt_df}
    )

    assert description.validate_description()
    assert np.isclose(description.owc, 1705.0)
    assert np.isclose(description.goc, 0)


if __name__ == "__main__":
    test_main()
    test_init_from_ecl_df()

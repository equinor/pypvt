"""Test element_fluid_description"""

import pathlib

import numpy as np
import pandas as pd
import ecl2df

from pypvt import ElementFluidDescription

TESTDATA = pathlib.Path(__file__).resolve().parent / "data"


def test_main():
    pass


def test_init_from_ecl_df():

    data_txt = (TESTDATA / "DATA").read_text(encoding="utf-8", errors="ignore")

    equil_txt = (TESTDATA / "equil").read_text(encoding="utf-8", errors="ignore")
    equil_df = ecl2df.equil.df(data_txt + equil_txt, keywords="EQUIL")

    rsvd_txt = (TESTDATA / "rsvd").read_text(encoding="utf-8", errors="ignore")
    rsvd_df = ecl2df.equil.df(data_txt + rsvd_txt, keywords="RSVD")

    rvvd_txt = (TESTDATA / "rvvd").read_text(encoding="utf-8", errors="ignore")
    rvvd_df = ecl2df.equil.df(data_txt + rvvd_txt, keywords="RVVD")

    pvt_txt = (TESTDATA / "pvt").read_text(encoding="utf-8", errors="ignore")
    pvt_df = ecl2df.pvt.df(data_txt + pvt_txt)

    description = ElementFluidDescription(1, 1)

    description.init_from_ecl_df(
        {
            "EQUIL": equil_df,
            "RSVD": rsvd_df,
            "RVVD": rvvd_df,
            "PVT": pvt_df,
            "PBVD": pd.DataFrame,
            "PDVD": pd.DataFrame,
        }
    )

    assert description.validate_description()
    assert np.isclose(description.owc, 1705.0)
    assert np.isclose(description.goc, 0)

    data_txt = (TESTDATA / "DATA").read_text(encoding="utf-8", errors="ignore")

    equil_txt = (TESTDATA / "equil").read_text(encoding="utf-8", errors="ignore")
    equil_df = ecl2df.equil.df(data_txt + equil_txt, keywords="EQUIL")

    pbvd_txt = (TESTDATA / "pbvd").read_text(encoding="utf-8", errors="ignore")
    pbvd_df = ecl2df.equil.df(data_txt + pbvd_txt, keywords="PBVD")

    pdvd_txt = (TESTDATA / "pdvd").read_text(encoding="utf-8", errors="ignore")
    pdvd_df = ecl2df.equil.df(data_txt + pdvd_txt, keywords="PDVD")

    pvt_txt = (TESTDATA / "pvt").read_text(encoding="utf-8", errors="ignore")
    pvt_df = ecl2df.pvt.df(data_txt + pvt_txt)

    description = ElementFluidDescription(1, 1)
    description.init_from_ecl_df(
        {
            "EQUIL": equil_df,
            "PBVD": pbvd_df,
            "PDVD": pdvd_df,
            "PVT": pvt_df,
            "RSVD": pd.DataFrame,
            "RVVD": pd.DataFrame,
        }
    )

    assert description.validate_description()
    assert np.isclose(description.owc, 1705.0)
    assert np.isclose(description.goc, 0)


def test_init_equil_from_df():

    txt = (TESTDATA / "DATA").read_text(encoding="utf-8", errors="ignore")

    txt += (TESTDATA / "equil").read_text(encoding="utf-8", errors="ignore")
    df = ecl2df.equil.df(txt, keywords="EQUIL")

    description = ElementFluidDescription(1, 1)

    description.init_equil_from_df(df)

    assert not description.validate_description()
    assert np.isclose(description.owc, 1705.0)
    assert np.isclose(description.goc, 0)


def test_init_rsvd_from_df():

    txt = (TESTDATA / "DATA").read_text(encoding="utf-8", errors="ignore")

    txt += (TESTDATA / "rsvd").read_text(encoding="utf-8", errors="ignore")
    df = ecl2df.equil.df(txt, keywords="RSVD")

    description = ElementFluidDescription(1, 1)

    description.init_rsvd_from_df(df)

    assert not description.validate_description()
    assert np.isclose(description.rsvd_rs[0], 184.0)


def test_init_rvvd_from_df():

    txt = (TESTDATA / "DATA").read_text(encoding="utf-8", errors="ignore")

    txt += (TESTDATA / "rvvd").read_text(encoding="utf-8", errors="ignore")
    df = ecl2df.equil.df(txt, keywords="RVVD")

    description = ElementFluidDescription(1, 1)

    description.init_rvvd_from_df(df)

    assert not description.validate_description()
    assert np.isclose(description.rvvd_rv[0], 0.5)


def test_init_pbvd_from_df():

    txt = (TESTDATA / "DATA").read_text(encoding="utf-8", errors="ignore")

    txt += (TESTDATA / "pbvd").read_text(encoding="utf-8", errors="ignore")
    df = ecl2df.equil.df(txt, keywords="PBVD")

    description = ElementFluidDescription(1, 1)

    description.init_pbvd_from_df(df)

    assert not description.validate_description()
    assert np.isclose(description.pbvd_pb[0], 360.0)


def test_init_pdvd_from_df():

    txt = (TESTDATA / "DATA").read_text(encoding="utf-8", errors="ignore")

    txt += (TESTDATA / "pdvd").read_text(encoding="utf-8", errors="ignore")
    df = ecl2df.equil.df(txt, keywords="PDVD")

    description = ElementFluidDescription(1, 1)

    description.init_pdvd_from_df(df)

    assert not description.validate_description()
    assert np.isclose(description.pdvd_pd[0], 60.0)


def test_get_df():

    txt = (TESTDATA / "DATA").read_text(encoding="utf-8", errors="ignore")

    txt += (TESTDATA / "pdvd").read_text(encoding="utf-8", errors="ignore")
    txt += (TESTDATA / "pbvd").read_text(encoding="utf-8", errors="ignore")
    txt += (TESTDATA / "rsvd").read_text(encoding="utf-8", errors="ignore")
    txt += (TESTDATA / "rvvd").read_text(encoding="utf-8", errors="ignore")

    df = ecl2df.equil.df(txt, keywords="PDVD")
    description = ElementFluidDescription(1, 1)
    description.init_pdvd_from_df(df)
    df_out = description.get_df("PDVD")

    assert len(df_out) == 2
    assert df["Z"][0] == df_out["Z"][0]
    assert df["PD"][1] == df_out["PD"][1]

    df = ecl2df.equil.df(txt, keywords="PBVD")
    description = ElementFluidDescription(1, 1)
    description.init_pbvd_from_df(df)
    df_out = description.get_df("PBVD")

    assert len(df_out) == 2
    assert df["Z"][0] == df_out["Z"][0]
    assert df["PB"][1] == df_out["PB"][1]

    df = ecl2df.equil.df(txt, keywords="RSVD")
    description = ElementFluidDescription(1, 1)
    description.init_rsvd_from_df(df)
    df_out = description.get_df("RSVD")

    assert len(df_out) == 2
    assert df["Z"][0] == df_out["Z"][0]
    assert df["RS"][1] == df_out["RS"][1]

    df = ecl2df.equil.df(txt, keywords="RVVD")
    description = ElementFluidDescription(1, 1)
    description.init_rvvd_from_df(df)
    df_out = description.get_df("RVVD")

    assert len(df_out) == 2
    assert df["Z"][0] == df_out["Z"][0]
    assert df["RV"][1] == df_out["RV"][1]


if __name__ == "__main__":
    test_main()
    test_init_from_ecl_df()
    test_init_equil_from_df()
    test_init_rsvd_from_df()
    test_init_rvvd_from_df()
    test_init_pbvd_from_df()
    test_init_pdvd_from_df()
    test_get_df()

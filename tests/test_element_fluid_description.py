"""Test element_fluid_description"""

import pathlib

import numpy as np
import ecl2df

from pypvt import ElementFluidDescription

TESTDATA = pathlib.Path(__file__).resolve().parent / "data"


def test_main():
    pass


def test_init_from_ecl_df():
    """
    Initialize instance with rsvd / rvvd from df
    """

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
            "PBVD": None,
            "PDVD": None,
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
            "RSVD": None,
            "RVVD": None,
        }
    )

    assert description.validate_description()
    assert np.isclose(description.owc, 1705.0)
    assert np.isclose(description.goc, 0)


if __name__ == "__main__":
    test_main()
    test_init_from_ecl_df()

"""Test element_fluid_description"""
#from __future__ import absolute_import

import os
import sys

import pandas as pd
import ecl2df

from pypvt import ElementFluidDescription

TESTDATA = os.path.join(os.path.dirname(__file__), "data")

def test_main():
    pass

def test_init_from_edl_df():
    txt = open(os.path.join(TESTDATA , "DATA"), 'r',encoding='utf-8', errors='ignore').read()
    txt += open(os.path.join(TESTDATA , "equil"), 'r',encoding='utf-8', errors='ignore').read()
    equil_df = ecl2df.equil.df(txt, keywords='EQUIL')

    txt = open(os.path.join(TESTDATA , "DATA"), 'r',encoding='utf-8', errors='ignore').read()
    txt += open(os.path.join(TESTDATA , "rsvd"), 'r',encoding='utf-8', errors='ignore').read()
    rsvd_df = ecl2df.equil.df(txt, keywords='RSVD')


    txt = open(os.path.join(TESTDATA , "DATA"), 'r',encoding='utf-8', errors='ignore').read()
    txt += open(os.path.join(TESTDATA , "rsvd"), 'r',encoding='utf-8', errors='ignore').read()
    rvvd_df = ecl2df.equil.df(txt, keywords='RSVD')

    equil_df = pd.merge(equil_df, rsvd_df, rvvd_df)

    txt = open(os.path.join(TESTDATA , "DATA"), 'r',encoding='utf-8', errors='ignore').read()
    txt += open(os.path.join(TESTDATA , "pvt"), 'r',encoding='utf-8', errors='ignore').read()

    pvt_df = ecl2df.pvt.df(txt)

    description = ElementFluidDescription(1,1)
    description.init_from_ecl_df(pvt_df, equil_df)

    pass


if __name__ == '__main__':
    print ('DEBUG')
    test_main()
    test_init_from_edl_df()

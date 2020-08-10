"""element_fluid_description module"""

import numpy as np
import pandas as pd


class element_fluid_description:
    """ A representation of black oil pvt and fluid contacts
    for a fluid system, valid for one specific equil number
    in an eclipse simulation deck.
    """

    def __init__ (
        self,
        eqlnum = 0,
        pvtnum = 0,
        rsvd_rs = None,
        rsvd_depth = None,
        owc = None,
        goc = None,

    ):
        self.pvtnum = pvtnum
        self.eqlnum = eqlnum
        self.rsvd_rs = rsvd_rs
        self.rsvd_depth = rsvd_depth
        self.owc = owc
        self.goc = goc


    def init_from_ecl_pd(self,pvt_df, eql_df):
        self.owc = eql_df[eql_df['EQLNUM']==self.eqlnum]['OWC'].unique()[0]
        self.goc = eql_df[eql_df['EQLNUM']==self.eqlnum]['GOC'].unique()[0]
        self.rsvd_rs = eql_df[eql_df['EQLNUM']==self.eqlnum]['RS'].dropna().to_numpy()
        self.rsvd_depth = eql_df[eql_df['EQLNUM']==self.eqlnum]['Z'].dropna().to_numpy()



    def validate_description (self):
        """
        check if the minimum requirements of a fluid description is fulfilled:

        """
        if not self.eqlnum:
            print ('EQILNUM not defined')
            return False

        if not self.pvtnum:
            print ('PVTNUM not defined')
            return False

        if not self.owc:
            print ('OWC not defined')
            return False

        if not self.goc:
            print ('GOC not defined')
            return False

        #if not self.rsvd_rs, (np.ndarray)):
        #    print ('RSVD not defined')
        #    return False
        #
        #if not type(self.rsvd_depth) == 'numpy.ndarray':
        #    print ('RSVD not defined')
        #    return False

        return True

import sys
import ecl2df
import pandas as pd

case = sys.argv[1]

def init_case(case_name):
    eclfiles = ecl2df.EclFiles(case_name)
    grid = ecl2df.grid.df(eclfiles)
    pvt = ecl2df.pvt.df(eclfiles)

    return eclfiles, grid, pvt



def main (case_name):
    eclfiles, grid, pvt = init_case(case_name)
    # TBD
    # loop over all equil regions
    # check consistency in pvt
    pass


if __name__ == '__main__':
    main(sys.argv[1])

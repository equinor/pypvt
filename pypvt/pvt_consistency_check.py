import sys

from pypvt import FieldFluidDescription


def main(case_name):

    fluid_description = FieldFluidDescription(ecl_case=case_name)

    print(fluid_description.validate_description())
    # print (fluid_description.fluid_descriptions[0].rvvd_rv)
    # print (fluid_description.fluid_descriptions[0].rvvd_depth)
    # loop over all equil regions
    # check consistency in pvt


if __name__ == "__main__":
    main(sys.argv[1])

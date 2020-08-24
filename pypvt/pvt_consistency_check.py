import sys

from pypvt import FieldFluidDescription


def main(case_name):

    fluid_description = FieldFluidDescription(ecl_case=case_name)

    print(fluid_description.validate_description())

    # loop over all equil regions
    # check consistency in pvt
    for fluid in fluid_description.fluid_descriptions:

        fluid.calc_fluid_prop_vs_depth(no_nodes=4)
        fluid.print_depth_tables()
        fluid.inplace_report()
        fluid.pvt_gradient_check()

if __name__ == "__main__":
    main(sys.argv[1])

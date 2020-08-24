import sys

from pypvt import FieldFluidDescription


def main(case_name):

    fluid_description = FieldFluidDescription(ecl_case=case_name)

    print(fluid_description.validate_description())
    for fluid in fluid_description.fluid_descriptions:
        fluid.calc_fluid_prop_vs_depth(no_nodes=2)
        fluid.inplace_report()
        fluid.pvt_gradient_check()


if __name__ == "__main__":
    main(sys.argv[1])

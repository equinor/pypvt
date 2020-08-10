import sys

from pypvt import field_fluid_description

def main (case_name):

    fluid_description = field_fluid_description.field_fluid_description(ecl_case=case_name)

    print(fluid_description.validate_description())

    # loop over all equil regions
    # check consistency in pvt
    pass


if __name__ == '__main__':
    main(sys.argv[1])

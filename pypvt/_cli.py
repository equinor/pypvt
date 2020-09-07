import argparse
import pathlib
from pypvt import FieldFluidDescription


def pvt_consistency_check(args: argparse.Namespace) -> None:
    """
    Entrypoint for running pypvt consistency checks.

    Args:
        args: input namespace from argparse

    Returns:
        Nothing
    """
    fluid_description = FieldFluidDescription(ecl_case=args.ecl_case)

    print(fluid_description.validate_description())
    for fluid in fluid_description.fluid_descriptions:
        fluid.calc_fluid_prop_vs_depth(no_nodes=args.nodes)
        fluid.inplace_report()
        fluid.pvt_gradient_check()


def main() -> None:
    """
    Main functionality run when the 'pypvt' command-line tool is called.
    """
    parser = argparse.ArgumentParser(description=("Command line interface for pypvt."))

    subparsers = parser.add_subparsers(
        help="The options available. "
        'Type e.g. "pypvt --help" '
        "to get help on that particular "
        "option."
    )

    parser_checks = subparsers.add_parser(
        "check", help="Run check and consistency algorithms on simulation and pvt data."
    )

    parser_checks.add_argument(
        "ecl_case",
        type=pathlib.Path,
        help="Path to Eclipse/Flow simulation case to check.",
    )

    parser_checks.add_argument(
        "-n",
        "--nodes",
        type=int,
        help="Number of depth nodes to be used in the calculation. (default = 20)",
        default=20,
    )

    parser_checks.set_defaults(func=pvt_consistency_check)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

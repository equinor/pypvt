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

    fluid_description = FieldFluidDescription(ecl_case=args.ecl_case, kwfile_dict={})

    print(fluid_description.validate_description())
    fnr = 0
    for fluid in fluid_description.fluid_descriptions:
        fluid.calc_fluid_prop_vs_depth(no_nodes=args.nodes)
        fluid.inplace_report()
        fluid.pvt_gradient_check()
        if fnr > 0:
            break
        fnr += 1
    fluid_description.create_consistency_report()


def pvt_consistency_adjustment(args: argparse.Namespace) -> None:
    """
    Entrypoint for running pypvt consistency adjustment,
    ie adjusting the xxvd tables to be consistent with
    respect to contacts.

    Args:
        args: input namespace from argparse

    Returns:
        Nothing
    """

    print("Running adjustment algorithm, more to come :)")
    kwfile_dict = {}
    if args.equil_file:
        kwfile_dict["EQUIL"] = args.equil_file
    if args.rsvd_file:
        kwfile_dict["RSVD"] = args.rsvd_file
    if args.rvvd_file:
        kwfile_dict["RVVD"] = args.rvvd_file
    if args.pbvd_file:
        kwfile_dict["PBVD"] = args.pbvd_file
    if args.pdvd_file:
        kwfile_dict["PDVD"] = args.pdvd_file
    if args.pvt_file:
        kwfile_dict["PVT"] = args.pvt_file
    fluid_description = FieldFluidDescription(
        ecl_case=args.ecl_case, kwfile_dict=kwfile_dict
    )

    print(fluid_description.validate_description())
    # fnr = 0
    # for fluid in fluid_description.fluid_descriptions:
    #    fluid.calc_fluid_prop_vs_depth(no_nodes=args.nodes)
    #    fluid.inplace_report()
    #    fluid.pvt_gradient_check()
    #    if fnr >0:
    #        break
    #    fnr +=1
    # fluid_description.create_consistency_report()


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

    parser_adjust = subparsers.add_parser(
        "adjust",
        help="Adjustment of rsvd/pbvd tables to make model consistent with respect to pvt.",
    )

    parser_adjust.add_argument(
        "--ecl_case",
        required=True,
        type=pathlib.Path,
        help="""Path to eclipse deck that has been run, eg a refcase,
        to read necessary kws from. Updated kws should be
        added by use of the optional arguments.""",
    )

    parser_adjust.add_argument(
        "--equil_file",
        type=pathlib.Path,
        help="File with updated equil kw to override the one from ecl_case",
    )

    parser_adjust.add_argument(
        "--pvt_file",
        type=pathlib.Path,
        help="File with updated pvt kw to override the one from ecl_case",
    )

    parser_adjust.add_argument(
        "--rsvd_file",
        type=pathlib.Path,
        help="File with rsvd kw to override the one from ecl_case",
    )

    parser_adjust.add_argument(
        "--rvvd_file",
        type=pathlib.Path,
        help="File with rvvd kw to override the one from ecl_case",
    )

    parser_adjust.add_argument(
        "--pbvd_file",
        type=pathlib.Path,
        help="File with PBVD kw to override the one from ecl_case",
    )

    parser_adjust.add_argument(
        "--pdvd_file",
        type=pathlib.Path,
        help="File with PDVD kw to override the one from ecl_case",
    )

    parser_adjust.add_argument(
        "--output",
        required=True,
        type=pathlib.Path,
        help="Name of consistent output table",
    )

    parser_adjust.set_defaults(func=pvt_consistency_adjustment)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

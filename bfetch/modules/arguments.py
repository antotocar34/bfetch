from typing import Tuple
import argparse as arg


def arguments() -> Tuple[bool, float]:
    parser = arg.ArgumentParser(description="Download files from blackboard")
    fast = 1.5
    slow = 0.1
    default = 0.8
    parser.add_argument(
        "-s",
        "--show",
        default=False,
        action="store_true",
        help="Whether to show the browser.",
    )
    parser.add_argument(
        "-S",
        "--slow",
        action="store_const",
        default=None,
        const=slow,
        help="Dowloads files at a slower sleep",
    )
    parser.add_argument(
        "-F",
        "--fast",
        action="store_const",
        default=None,
        const=fast,
        help="Downloads the files as fast as possible.",
    )
    args = parser.parse_args()

    if args.slow:
        speed = args.slow
    elif args.fast:
        speed = args.fast
    else:
        speed = default

    return args.show, speed

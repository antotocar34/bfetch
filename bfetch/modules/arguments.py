import argparse as arg

def parse_args():
    """Parses Argument given"""
    parser = arg.ArgumentParser(description="Download files from blackboard")
    fast = 1.5
    slow = 0.1
    default = 0.8
    parser.add_argument("-s", "--show", action="store_false")
    parser.add_argument("-S", action="store_const", default=default, const=fast)
    parser.add_argument("-F", action="store_const", default=default, const=slow)
    args = parser.parse_args()
    return args

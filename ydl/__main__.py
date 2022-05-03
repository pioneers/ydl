import sys
from ._core import run_ydl_server




def print_help_message():
    s = """
Usage: ydl [-h] [-v] [-a address] [-p port]

Command-line options:
     -h --help
        Display a help message and exit
     -v --verbose
        Print whenever a client connects or disconnects
     -a --address address
        Run server on specified ip address, such as 0.0.0.0
     -p --port port
        Run server on specified port 
    """
    print(s)




if __name__ == "__main__":

    flags = {
        "verbose": False,
        "help": False,
    }
    arg_flags = {
        "address": None,
        "port": None,
    }
    short_flags = {
        "v":"verbose",
        "h": "help",
        "a":"address",
        "p":"port",
    }

    ind = 1
    usage_error = None
    while ind < len(sys.argv):
        onedash = sys.argv[ind].startswith("-")
        twodash = sys.argv[ind].startswith("--")
        f = None
        if onedash and not twodash:
            if sys.argv[ind][1:] in short_flags:
                f = short_flags[sys.argv[ind][1:]]
            else:
                usage_error = f"Short flag not recognized: {sys.argv[ind]}"
                break;
        elif onedash:
            f = sys.argv[ind][2:]
        
        if f is not None:
            if f in flags:
                flags[f] = True
            elif f in arg_flags:
                ind += 1
                if ind < len(sys.argv) and not sys.argv[ind].startswith("-"):
                    arg_flags[f] = sys.argv[ind]
                else:
                    usage_error = f"No argument for: {f}"
                    break
            else:
                usage_error = f"Flag not recognized: {f}"
                break
        else:
            # regular arg, but ydl has none
            usage_error = f"Parameter not recognized: {sys.argv[ind]}"
            break;
        ind += 1

    if usage_error is not None:
        print("Error:", usage_error)
        print_help_message()
    elif flags["help"]:
        print_help_message()
    else:
        p = None
        good = True
        if arg_flags["port"] is not None:
            try:
                p = int(arg_flags["port"])
            except ValueError:
                print(f"Error parsing port number: {arg_flags['port']}")
                good = False
        if good:
            run_ydl_server(arg_flags["address"], p, flags["verbose"])

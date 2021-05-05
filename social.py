from src.instagram import Instagram
import argparse
import sys
import signal
from rich.console import Console 

pc = Console()


is_windows = False

try:
    import gnureadline
except:
    is_windows = True
    import pyreadline

def list_all_commands():
    pc.print("FILE=y/n\t", style="white")
    print("Enable/disable output in a '<target_username>_<command>.txt' file")
    pc.print("JSON=y/n\t", style="white")
    print("Enable/disable export in a '<target_username>_<command>.json' file")
    pc.print("addrs\t\t", style="skyblue")
    print("Get all addresses by pinned by  Target")
    pc.print("caption\t\t", style="red")
    print("Get target's photos captions")
    pc.print("comments\t\t", style="red")
    print("Get all comments by Target")



def signal_handler(sig, frame):
    pc.print("\nGoodbye\n", style="red")
    sys.exit(0)

def completer(text, state):
    options = [i for i in commands if i.startswith(text)]

    if state < len(options):
        return options[state]
    else:
        return None

def _exit():
    pc.print("Exiting..\n", style="red")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if is_windows:
    pyreadline.Readline().parse_and_bind("tab: complete")
    pyreadline.Readline().set_completer(completer)

else:
    gnureadline.parse_and_bind("tab: complete")
    gnureadline.set_completer(completer)


parser = argparse.ArgumentParser(description="Superior Domination ")
parser.add_argument('id', type=str, help='username')
parser.add_argument('-j', '--json', help='Store result in Json File.', action='store_true')
parser.add_argument('-f', '--file', help='Store result in a file', action='store_true')

args = parser.parse_args()
api = Instagram(args.id, args.file, args.json)


signal.signal(signal.SIGINT, signal_handler)
gnureadline.parse_and_bind("tab: complete")
gnureadline.set_completer(completer)



commands = {

        'ls': list_all_commands,
        'help': list_all_commands,
        'quit': _exit,
        'exit': _exit,
        'addrs': api.get_addrs,
        'captions': api.get_captions,
        'comments':api.get_total_comments,

}








while True:
    pc.print("Run a command: ", style="yellow")
    cmd = input()

    _cmd = commands.get(cmd)

    if _cmd:
        _cmd()
    elif cmd == "FILE=y":
        api.set_write_file(True)
    elif cmd == "FILE=n":
        api.set_write_file(False)
    elif cmd == "JSON=y":
        api.set_json_dump(True)
    elif cmd == "JSON=n":
        api.set_json_dump(False)
    elif cmd == "":
        print("")
    else:
        pc.print("Unrecognized Command\n", style="red")


    

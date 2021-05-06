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
    pc.print("locations\t\t", style="blue")
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

commands = {

        'ls': list_all_commands,
        'help': list_all_commands,
        'quit': _exit,
        'exit': _exit,
        'locations': api.target_locations,
        #'captions': api.get_captions,
        #'comments':api.get_total_comments,

}


signal.signal(signal.SIGINT, signal_handler)
gnureadline.parse_and_bind("tab: complete")
gnureadline.set_completer(completer)

while True:
    #pc.print("command: ", style="yellow")
    cmd = input("Command :")

    _cmd = commands.get(cmd)

    if _cmd:
        list_all_commands()
    elif cmd == "FILE=y":
        api.write_file(True)
    elif cmd == "FILE=n":
        api.write_file(False)
    elif cmd == "JSON=y":
        api.json_dump(True)
    elif cmd == "JSON=n":
        api.json_dump(False)
    elif cmd == "":
        print("")
    else:
        pc.print("Unrecognized Command\n", style="red")


    

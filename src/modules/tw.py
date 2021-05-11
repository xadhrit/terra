import argparse
import sys
import signal
from rich import style
from rich.console import Console, get_windows_console_features
from twittr import Twitter

pc = Console()
is_wind = sys.platform.startswith('win')

if is_wind:
    import pyreadline
    
else:
    import gnureadline
    
pc.print("Testing Twitter Module..", style="yellow")


def list_all_commands():
    pc.print("tweets\t\t",style="red")
    print("\nGet Recent Tweets of Target")
    pc.print("fav\t\t", style="yellow")
    print("\n Get total Favourites of target")
    pc.print("followers\t\t", style="white")
    print("\n Get total followers of Target")
    pc.print("followings\t\t", style="cyan")
    print("\n Get total followings of target")
    pc.print("list\t\t", style="green")
    print("\n Get list of target's list")
    
def handle_single(sig, frame):
    pc.print("\n Sending you Out \n", style="red")
    sys.exit(0)
    

def completer(text, state):
    options = [i for i in commands if i.startswith(text)]
    if state < len(options):
        return options[state]
    
    else:
        return None
    
def _out():
    pc.print("Thank you for using Terra!", style="yellow")
    sys.exit(0)
    
signal.signal(signal.SIGINT, handle_single)

if is_wind:
    pyreadline.Readline().parse_and_bind("tab: complete")
    pyreadline.Readline().set_completer(completer)
    
else:
    gnureadline.parse_and_bind("tab: complete") 
    gnureadline.set_completer(completer) 
    

parser = argparse.ArgumentParser(description="Testing Twitter Module")
parser.add_argument('target', type=str, help='username of target')
#parser.add_argument('-j', '--json', help='save results in a JSON file', action='store_true')
#parser.add_argument('-f', '--file', help='save results in a Text File', action='store_true')

args = parser.parse_args()   

api = Twitter(args.target)

commands = {
    'ls': list_all_commands,
    'help': list_all_commands,
    'quit': quit,
    'exit': _out,
    'tweets': api.recent_tweets, 
    'fav': api.total_fav,
    'followers': api.get_followers,
    'following': api.get_frnds,
    'list': api.get_list
    
}

signal.signal(signal.SIGINT, handle_single)
gnureadline.parse_and_bind("tab: complete")
gnureadline.set_completer(completer)

while True:
    pc.print("Terra Command : ", style="cyan")
    user_input = input()
    
    cmd = commands.get(user_input)
    
    if cmd:
        cmd()
    elif user_input == "":
        print("")
    else:
        pc.print("ILLEGAL COMMAND\n", style='red')
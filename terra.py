import argparse
import sys
import os
import signal
from rich.console import Console
from src.twittr import Twitter

pc = Console()

is_wind = sys.platform.startswith('win' or 'nt')


if is_wind:
    import pyreadline

else:
    import gnureadline


def banner():

    pc.print("                 _ _________________________                                                                           ", style="green")
    pc.print("                /          2021             /                                                                          ", style="green")
    pc.print("               /__________       __________/ _______    ___________________________________________  _______           ", style="green")
    pc.print("                          / b  /       /            \  /               /               /                    /          ", style="green")
    pc.print("                         / y: /       /    ______    \/     __________/     __________/   _   _____        /           ", style="green")
    pc.print("                        /    /       /   A  D  H  R  I  T /         /    /          /    /         /      /            ", style="green")
    pc.print("                       /    /       /      ________ /    /         /    /          /    /         /      /             ", style="green")
    pc.print("                      /    /       /               /    /         /    /          /    /_________/      /              ", style="green")
    pc.print("                     /    /        \              /    /         /    /            \                   /               ", style="green")
    pc.print("                    /    /          \____________/____/         /____/              \____________/ \__/                ", style="green")
    pc.print("                   /___ /                                                                                              ", style="green")
    pc.print("                                     OSINT TOOL ON SOCIAL MEDIA NETWORKS                                                                                              ", style="cyan1")
    print(" ")
    pc.print("                                     @xadhrit (github.com/xadhrit/)                                                                                                                                 " , style="bright_red")

banner()

def list_all_commands():
    pc.print("FILE=y/n : ", style="yellow", end='')
    print(" Enable/disable output in a '<target username>_<command>.txt' file")
    pc.print("JSON=y/n :  \t", style="white", end='')
    print("Enable/disable export in a '<target username>_<command>.json' file'")
    pc.print("tweets\t : ", style="bright_cyan", end='')
    print("Get recent tweets of target")
    pc.print("favtweets : \t", style="yellow", end='')
    print("Get recent tweets which are liked by target")
    pc.print("followers : \t", style="bright_green", end='')
    print(" Get total followers of Target")
    pc.print("following : \t", style="cyan", end='')
    print("Get total followings of target")
    pc.print("reset target : \t", style='green', end='')
    print(" Select new target")
    pc.print("info : \t", style="dark_cyan", end='')
    print("Full information of target's account")
    pc.print("profile pic : ", style='bright_magenta', end='')
    print("Download Target's Profile Picture")
    pc.print("banner : ", style='steel_blue1', end='')
    print("Download Target's Profile Banner ")
    pc.print('htags : ', style='bright_red', end='')
    print('Get hashtags used by target')
    print(" ")
    pc.print(" Also supports basic terminal commands : ", style='cyan')
    pc.print("ls : ", style='pink1', end='')
    pc.print("Displaying all Commands ", ":search:", style='bright_white')
    pc.print("exit : ", style='orange_red1', end='')
    pc.print("For Exit from Terra", style='bright_white')
    pc.print("clear: ", style='orchid2', end='')
    pc.print("Clear your Screen", style='bright_white')

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

def clear():
    # for windows screen
    if is_wind:
        os.system('cls')

    # for mac or linux screen
    else:
        os.system('clear')

signal.signal(signal.SIGINT, handle_single)

if is_wind:
    pyreadline.Readline().parse_and_bind("tab: complete")
    pyreadline.Readline().set_completer(completer)

else:
    gnureadline.parse_and_bind("tab: complete")
    gnureadline.set_completer(completer)

parser = argparse.ArgumentParser(description="Recon with Terra")
parser.add_argument('username', type=str, help='username of target')
parser.add_argument('-j', '--json', help='save results in a JSON file', action='store_true')
parser.add_argument('-f', '--file', help='save results in a Text File', action='store_true')
args = parser.parse_args()
api = Twitter(args.username, args.file, args.json)

commands = {
        'ls': list_all_commands,
        'help': list_all_commands,
        'quit': quit,
        'clear': clear,
        'exit': _out,
        'reset target': api.reset_target,
        'tweets': api.recent_tweets,
        'favtweets': api.recent_fav,
        'followers': api.get_followers,
        'following': api.get_frnds,
        'info': api.user_info,
        'profile pic': api.profile_pic,
        'banner': api.banner_pic,
        'htags': api.get_hashtags

}

signal.signal(signal.SIGINT, handle_single)
gnureadline.parse_and_bind("tab: complete")
gnureadline.set_completer(completer)

while True:
    pc.print("\n Terra Command : ", style="cyan", end='')
    user_input = input()

    cmd = commands.get(user_input)

    if cmd:
        cmd()
    elif user_input == "FILE=y":
        api.write_file(True)
    elif user_input == "FILE=n":
        api.write_file(False)
    elif user_input == "JSON=y":
        api.json_dump(True)
    elif user_input == "JSON=n":
        api.json_dump(False)
    elif user_input == "":
        print("")
    else:
        pc.print("ILLEGAL COMMAND\n", style='red')

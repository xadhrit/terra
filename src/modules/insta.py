import sys , os
import signal
from rich.console import Console
import argparse
from instagram import Instagram


pc = Console()

is_wind = os.name.startswith('win' or 'nt')

if is_wind:
    import pyreadline

else:
    import gnureadline
    
#pc.print("Just Testing..", style="red")


def list_all_commands():
    
    pc.print("FILE=y/n : ", style="yellow",end='')
    print(" Enable/disable output in a '<target username>_<command>.txt' file")
    pc.print("JSON=y/n :  \t", style="white", end='')
    print("Enable/disable export in a '<target username>_<command>.json' file'")
    pc.print("locations :  \t", style="green", end='')
    print("Get all registered addressed by target photos")
    pc.print("captions : \t", style="cyan", end='')
    print("Get target's photos captions")
    pc.print("comments : \t", style="red", end='')
    print("Get total comments of target's posts")
    pc.print("followers : \t", style="yellow", end='')
    print("get target's followers")
    pc.print("followings : \t", style="red", end='')
    print("Get users followed by target")
    pc.print("followers emails :  \t", style="green", end='')
    print("Get email of target followers")
    pc.print("following emails :  \t", style="yellow", end='')
    print("Get email of users followed by target")
    pc.print("followers  phone :  \t", style="red", end='')
    print("Get phone number of target followers")
    pc.print("followings phone :  \t" ,style="cyan", end='')
    print("Get phone number of users followed by target")
    pc.print("tags : \t", style="yellow", end='')
    print("Get hashtags used by target")
    pc.print("info : \t", style="white", end='')
    print("Target  timeline and information")
    pc.print("likes : \t", style="red", end='')
    print("Get total likes of target's posts")
    pc.print("mediatype :  \t", style="green", end='')
    print("Get target's posts type (photo or video)")
    pc.print("photodes :  \t", style="cyan", end='')
    print("Get description of target's photos")
    pc.print("photos  : \t", style="yellow", end='')
    print("Download target's photos in output folder")
    pc.print("profile pic :  \t", style="white", end='')
    print("Download target's profile picture")
    pc.print("stories : \t", style="cyan", end='')
    print("Download target's stories")
    pc.print("tagged  :  \t", style="red", end='')
    print("Get list of users tagged by target")
    pc.print("reset target : \t\t", style="white", end='')
    print("Set new target")
    pc.print("commenter : \t", style="red", end='')
    print("Get a list of user who commented target's photos")
    pc.print("ttag  :  \t", style="green", end='')
    print("Get a list of user who tagged target")
    print(" ")
    pc.print(" Also supports basic terminal commands : ", style='cyan')
    pc.print("ls : ", style='pink1', end='')
    pc.print("Displaying all Commands ", ":search:", style='bright_white')
    pc.print("exit : ", style='orange_red1', end='')
    pc.print("For Exit from Terra", style='bright_white')
    pc.print("clear: ", style='orchid2', end='')
    pc.print("Clear your Screen", style='bright_white')
    
    
    
    
     
def handle_single(sig, frame):
    pc.print("\nThroughing You Out\n", style="red")
    sys.exit(0)
    
def completer(text, state):
    options = [i for i in commands if i.startswith(text)]
    if state < len(options):
        return options[state]
    
    else:
        return None
    
def _out():
    pc.print("Thank you for using Terra!", style="bright_yellow")
    sys.exit(0)
    
def clear():
    if is_wind:
        os.system('cls')
        
    else:
        os.system('clear')
        
    
signal.signal(signal.SIGINT, handle_single)

if is_wind:
    pyreadline.Readline().parse_and_bind("tab: complete")
    pyreadline.Readline().set_completer(completer)
    
else:
    gnureadline.parse_and_bind("tab: complete")
    gnureadline.set_completer(completer)

parser = argparse.ArgumentParser(description='Recon with Terra')
parser.add_argument('id', type=str, help='username of target')
parser.add_argument('-j', '--json', help='save results in a JSON file', action='store_true')
parser.add_argument('-f', '--file', help='save results in a Text File', action='store_true')

args = parser.parse_args()

api = Instagram(args.id, args.file, args.json)

commands = {
    'ls': list_all_commands,
    'help': list_all_commands,
    'clear': clear,
    'quit' : quit,
    'exit': _out,
    'locations': api.target_locations,
    'captions':api.__getCaptions__,
    'reset target': api.change_target,
    'comments': api._all_comments,
    'followers': api._followers,
    'followings': api._followings,
    'followers emails': api.followers_email,
    'following emails': api.followings_email,
    'followers phone' : api.followers_phoneNumber,
    'followings phone': api.followings_phoneNumber,
    'tags':api._hashtags,
    'timeline':api._user_timeline,
    'likes': api._total_likes,
    'mediatype': api._media_type,
    'photodes': api._photo_description,
    'photos': api._user_photo,
    'profile pic': api._user_profilepic,
    'stories': api._user_stories,
    'tagged': api._people_who_tagged_by_target,
    'commenter':  api._people_who_commented,
    'ttag': api._users_who_tagged
}

signal.signal(signal.SIGINT, handle_single)
gnureadline.parse_and_bind("tab : complete")
gnureadline.set_completer(completer)

while True:
    pc.print("Terra Command : ", style="cyan", end='')
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




    
    
    



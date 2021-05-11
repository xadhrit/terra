import sys
import signal
from rich.console import Console
import argparse
from instagram import Instagram


pc = Console()
is_wind = sys.platform.startswith('win')


if is_wind:
    import pyreadline

else:
    import gnureadline
    
pc.print("Just Testing..", style="red")


def list_all_commands():
    pc.print("FILE=y/n\t", style="yellow")
    print("Enable/disable output in a '<target username>_<command>.txt' file'")
    pc.print("JSON=y/n\t", style="white")
    print("Enable/disable export in a '<target username>_<command>.json' file'")
    pc.print("locations\t\t", style="green")
    print("Get all registered addressed by target photos")
    pc.print("captions\t", style="cyan")
    print("Get target's photos captions")
    pc.print("comments\t", style="red")
    print("Get total comments of target's posts")
    pc.print("followers\t", style="yellow")
    print("get target's followers")
    pc.print("followings\t", style="red")
    print("Get users followed by target")
    pc.print("followers emails\t", style="green")
    print("Get email of target followers")
    pc.print("following emails\t", style="yellow")
    print("Get email of users followed by target")
    pc.print("followers  phone\t", style="red")
    print("Get phone number of target followers")
    pc.print("followings phone\t" ,style="cyan")
    print("Get phone number of users followed by target")
    pc.print("tags\t", style="yellow")
    print("Get hashtags used by target")
    pc.print("timeline\t\t", style="white")
    print("Target  timeline and information")
    pc.print("Posts\t\t", style="green")
    print("Get total number of posts of target.")
    pc.print("likes\t\t", style="red")
    print("Get total likes of target's posts")
    pc.print("mediatype\t", style="green")
    print("Get target's posts type (photo or video)")
    pc.print("photodes\t", style="cyan")
    print("Get description of target's photos")
    pc.print("photos\t\t", style="yellow")
    print("Download target's photos in output folder")
    pc.print("profile pic\t\t", style="white")
    print("Download target's profile picture")
    pc.print("stories\t\t", style="cyan")
    print("Download target's stories")
    pc.print("tagged\t\t", style="red")
    print("Get list of users tagged by target")
    pc.print("reset target\t\t", style="white")
    print("Set new target")
    pc.print("commenter\t", style="red")
    print("Get a list of user who commented target's photos")
    pc.print("ttag\t\t", style="green")
    print("Get a list of user who tagged target")
     
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
    pc.print("Thank you for using Terra!", style="red")
    sys.exit(0)
    

signal.signal(signal.SIGINT, handle_single)

if is_wind:
    pyreadline.Readline().parse_and_bind("tab: complete")
    pyreadline.Readline().set_completer(completer)
    
else:
    gnureadline.parse_and_bind("tab: complete")
    gnureadline.set_completer(completer)

parser = argparse.ArgumentParser(description='terra instagram module testing')
parser.add_argument('id', type=str, help='username of target')
parser.add_argument('-j', '--json', help='save results in a JSON file', action='store_true')
parser.add_argument('-f', '--file', help='save results in a Text File', action='store_true')

args = parser.parse_args()

api = Instagram(args.id, args.file, args.json)

commands = {
    'ls': list_all_commands,
    'help': list_all_commands,
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
    pc.print("Terra Command : ", style="cyan")
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




    
    
    



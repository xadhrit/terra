import argparse
import sys
import os
from rich.console import Console
from pyfiglet import Figlet
from rich.style import Style
from src.instagram import Instagram
from src.twittr import Twitter
import signal
import pyreadline3 as pyreadline

pc = Console()

is_wind = sys.platform.startswith('win' or 'nt')


def twitter_all_commands():
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
    pc.print("timeline : \t", style="dark_cyan", end='')
    print("Full information of target's account")
    pc.print("profile pic : ", style='bright_magenta', end='')
    print("Download Target's Profile Picture")
    pc.print("banner : ", style='steel_blue1', end='')
    print("Download Target's Profile Banner ")
    pc.print('htags : ', style='bright_red', end='')
    print('Get hashtags used by target')
    pc.print('mentions : ', style='pink1')
    print('Get users who got mentioned by target in recent tweets')
    print(" ")
    pc.print(" Also supports basic terminal commands : ", style='cyan')
    pc.print("ls : ", style='pink1', end='')
    pc.print("Displaying all Commands ", ":search:", style='bright_white')
    pc.print("exit : ", style='orange_red1', end='')
    pc.print("For Exit from Terra", style='bright_white')
    pc.print("clear : ", style='orchid2', end='')
    pc.print("Clear your Screen", style='bright_white')
    pc.print('back : ', style='purple', end='')
    pc.print('Back to Main Menu', style='yellow')




def insta_all_commands():
    
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
    pc.print("clear : ", style='orchid2', end='')
    pc.print("Clear your Screen", style='bright_white')
    pc.print('back : ', style='purple', end='')
    pc.print('Back to Main Menu', style='yellow')
    


def clear():
    # for windows screen
    if is_wind:
        os.system('cls')

    # for mac or linux          
    else:
        os.system('clear')
        
        
def banner():
    clear()
    banner = Figlet(font='isometric3',justify='right')
    pc.print(banner.renderText("Terra"),style="bold red")
    pc.print("                         OSINT TOOL ON SOCIAL MEDIA NETWORKS                                                                                              ", style="cyan1")
    print(" ")
    pc.print("                         @xadhrit (github.com/xadhrit/)                         " , style='bold red')                                                   


def _out():
    pc.print("Thank you for using Terra!", style="yellow")
    sys.exit(0)


def handle_single(sig, frame):
    pc.print("\n Sending you Out \n", style="red")
    sys.exit(0)

parser = argparse.ArgumentParser(description="Recon with Terra")        
parser.add_argument('target', type=str, help='username of target')
parser.add_argument('-j', '--json', help='save results in a JSON file', action='store_true')
parser.add_argument('-f', '--file', help='save results in a Text File', action='store_true')
args = parser.parse_args()


def main():
    banner()    
    pc.print("  \n> 1 for Twitter ",style="bright_yellow")
    pc.print("  \n> 2 for Instagram ",style="green3")
    pc.print("  \n> 3 for Exit ")
    print(" ")
    pc.print("> Choose one option : ",style='purple',end='')
    u_input = str(input())
    #print(u_input)
    try:
        if u_input == '1':
            def completer(text, state):
                options = [i for i in commands if i.startswith(text)]
                #print(options)
                if state < len(options):
                    return options[state]

                else:
                    return None

            signal.signal(signal.SIGINT, handle_single)
                            
            pyreadline.Readline().parse_and_bind("tab: complete")
            pyreadline.Readline().set_completer(completer)
                        
            parser = argparse.ArgumentParser(description="Recon with Terra")        
            parser.add_argument('target', type=str, help='username of target')
            parser.add_argument('-j', '--json', help='save results in a JSON file', action='store_true')
            parser.add_argument('-f', '--file', help='save results in a Text File', action='store_true')
            args = parser.parse_args()
            api = Twitter(args.target,args.file,args.json)
            
                       
            commands = {
                'ls': twitter_all_commands,
                'help': twitter_all_commands,
                'quit': quit,
                'clear': clear,
                'exit': _out,
                 'back': main,
                'reset target': api.reset_target,
                'tweets': api.recent_tweets,
                'favtweets': api.recent_fav,
                'followers': api.get_followers,
                'following': api.get_frnds,
                'timeline': api.user_info,
                'profile pic': api.profile_pic,
                'banner': api.banner_pic,
                'htags': api.get_hashtags,
                'mentions':api.get_mentions

            }
            signal.signal(signal.SIGINT, handle_single)
            pyreadline.parse_and_bind("tab: complete")
            pyreadline.set_completer(completer)
            
            while True:
                print(" ")
                pc.print("~/Terra Command >$ ", style='purple', end='')
                user_input = input()
                
                cmd = commands.get(user_input)
                if cmd:
                    cmd()
                    
                elif user_input == 'FILE=y':
                    api.write_file(True)
                
                elif user_input == 'FILE=n':
                    api.write_file(False)
                    
                elif user_input == 'JSON=y':
                    api.json_dump(True)
                    
                elif user_input == 'JSON=n':
                    api.json_dump(False)
                    
                elif user_input == '':
                    print("")
                    
                else:
                    pc.print("ILLEGAL COMMAND", style="red")                  
      
        
        if u_input == '2':
            def completer(text, state):
                options = [i for i in commands if i.startswith(text)]
                print(options)
                if state < len(options):
                    return options[state]

                else:
                   return None
               
            signal.signal(signal.SIGINT, handle_single)
            
            
            pyreadline.Readline().parse_and_bind("tab: complete")
            pyreadline.Readline().set_completer(completer)
                           
            parser = argparse.ArgumentParser(description="Recon with Terra")        
            parser.add_argument('target', type=str, help='username of target')
            parser.add_argument('-j', '--json', help='save results in a JSON file', action='store_true')
            parser.add_argument('-f', '--file', help='save results in a Text File', action='store_true')
            args = parser.parse_args()
            api = Instagram(args.target,args.file,args.json)
            
                                                                                                                      

            commands = {
            'ls': insta_all_commands,
            'help': insta_all_commands,
            'clear': clear,
            'quit': quit,
            'exit': _out,
            'back' : main,
            'locations': api.target_locations,
            'captions': api.__getCaptions__,
            'reset target': api.change_target,
            'comments': api._all_comments,
            'followers': api._followers,
            'followings': api._followings,
            'followers emails': api.followers_email,
            'following emails': api.followings_email,
            'followers phone': api.followers_phoneNumber,
            'followings phone': api.followings_phoneNumber,
            'tags': api._hashtags,
            'timeline': api._user_timeline,
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
            pyreadline.parse_and_bind("tab: complete")
            pyreadline.set_completer(completer)
            
            while True:
                pc.print("~/Terra Command >$ ", style='purple', end='')
                user_input = input()
                
                cmd = commands.get(user_input)
                if cmd:
                    cmd()
                    
                elif user_input == 'FILE=y':
                    api.write_file(True)
                
                elif user_input == 'FILE=n':
                    api.write_file(False)
                    
                elif user_input == 'JSON=y':
                    api.json_dump(True)
                    
                elif user_input == 'JSON=n':
                    api.json_dump(False)
                    
                elif user_input == '':
                    print("")
                    
                else:
        
                    pc.print("ILLEGAL COMMAND", style="red")
        
        if u_input == '3':
            sys.exit(0)
        
        if KeyboardInterrupt:
            pc.print('Invalid Option! Try Again.... ', style='bold red')
            pc.print('Do you want to choose again ? (y/n)', style='red')
            io = input()
            if io == 'y' or 'Y':
                main()
            if io == 'n' or 'N':
                sys.exit(0)
            else:
                print('Not a option! Good Bye!')
                sys.exit(0)
        
        else:
            pc.print('Invalid Option! ',style='bright_red')
            main()
                
    except Exception as e:
        pc.print(e,style='orange1')        
    
if __name__ == '__main__':
    main()    


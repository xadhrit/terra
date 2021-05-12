"""

API Key: 7np6DuME8eguQJ1A0iYrefzaQ
API Secret Key: 6AuPpib8uJGnKDdA9nJcDnnHWWajfNiqsHIxH5j6E7rXyrG9nZ

Bearer Token: AAAAAAAAAAAAAAAAAAAAAHQSPAEAAAAAS1HmIEOispsWLiT%2FGgHSHK63Cc4%3DWYNvWWDwhfvcBwOkQC3ySRTEfmEkocdZDOq7bRnTeDoo1D1zsH

Access Token: 1291638708110651392-T00PIQffV3zCEB5VjPUo9Zi6ziCGdq

Access Token: fDraPtVcJ0SX71ncPPwiNINHsyzdlEsJNpwkFT2Gd6PbF
"""

import urllib
import sys
import json
import os
import codecs
import requests
from prettytable import PrettyTable
import twitter
from rich.console import Console
from twitter import TwitterError

pc = Console()


class Twitter:
    api = None
    api2 = None
    #eolocator = Nominatim(user_agent="http")
    #ser_id =None
    #tatus = None
    #riends = None
    #target = ""
    target = ""
    writeFile = False
    jsonDump = False

    def __init__(self,target):
    
        self.api = twitter.Api(consumer_key='7np6DuME8eguQJ1A0iYrefzaQ',consumer_secret='6AuPpib8uJGnKDdA9nJcDnnHWWajfNiqsHIxH5j6E7rXyrG9nZ',access_token_key='1291638708110651392-T00PIQffV3zCEB5VjPUo9Zi6ziCGdq',access_token_secret='fDraPtVcJ0SX71ncPPwiNINHsyzdlEsJNpwkFT2Gd6PbF')
        pc.print("\nValidating Your Credentials...", style="cyan")
        self.__verifyCreds__()
        self.__setTarget__(target)
        #self.writeFile = is_file
        #self.js ap api = twitter.Api(consumer_key='7np6DuME8eguQJ1A0iYrefzaQ',consumer_secret='6AuPpib8uJGnKDdA9nJcDnnHWWajfNiqsHIxH5j6E7rXyrG9nZ',access_token_key='1291638708110651392-T00PIQffV3zCEB5VjPUo9Zi6ziCGdq',access_token_secret='fDraPtVcJ0SX71ncPPwiNINHsyzdlEsJNpwkFT2Gd6PbF')i = twitter.Api(consumer_key='7np6DuME8eguQJ1A0iYrefzaQ',consumer_secret='6AuPpib8uJGnKDdA9nJcDnnHWWajfNiqsHIxH5j6E7rXyrG9nZ',access_token_key='1291638708110651392-T00PIQffV3zCEB5VjPUo9Zi6ziCGdq',access_token_secret='fDraPtVcJ0SX71ncPPwiNINHsyzdlEsJNpwkFT2Gd6PbF')onFile = is_json
    
    
    
    def __verifyCreds__(self):
        result = []
         
        api = twitter.Api(consumer_key='7np6DuME8eguQJ1A0iYrefzaQ',consumer_secret='6AuPpib8uJGnKDdA9nJcDnnHWWajfNiqsHIxH5j6E7rXyrG9nZ',access_token_key='1291638708110651392-T00PIQffV3zCEB5VjPUo9Zi6ziCGdq',access_token_secret='fDraPtVcJ0SX71ncPPwiNINHsyzdlEsJNpwkFT2Gd6PbF')
        result = api.VerifyCredentials()
        #print(result)
        my_name = result.screen_name
        pc.print("logged in as: ", my_name, style="green")
        #data.extend(result.description)
        #print(result)
        return 
    #__verifyCreds__()
   
    def write_file(self, flag):
        if flag:
           pc.print("Write to file : ", style="yellow")
           pc.print("enabled" , style="green")
           pc.print("\n")

        else:
           pc.print("Export to JSON :", style="red")
           pc.print("disabled, ", style="red")
           pc.print("\n")

        self.writeFile = flag
    
    def json_dump(self, flag):
        if flag:
            pc.print("Export to JSON: ", style="yellow")
            pc.print("enabled", style="green")
            pc.print("\n")

        else:
            pc.print("Export to JSON : ", style="red")
            pc.print("disabled", style="red")
            pc.print("\n")

        self.jsonDump = flag

    def to_json(self, python_object):
        if isinstance(python_object, bytes):
            return {'__class__':'bytes', '__value__':codecs.encode(python_object, 'base64').decode()
            }
        raise TypeError(repr(python_object) + 'is not JSON parseable !')
    
        
    def from_json(self, json_object):
        if  '__class__' in json_object and json_object['__class__'] == 'bytes':
            return codecs.decode(json_object['__value__'].encode(), 'base64')
        return json_object
            
    
    
    def recent_tweets(self):
        tweets = self.api.GetUserTimeline(screen_name=self.target)
        for t in tweets:
            pc.print(t, style="yellow")
        return    
    
    
    
    def get_user(self):
        try:
            data = self.api.GetUser(screen_name=self.target)
            print(data)
            pc.print("\n Target's Information: \n", style='green')
            pc.print("\n Username : {} , id : {} ".format(data.screen_name,data.id),style='yellow')
            pc.print("\n Joined on : ", data.created_at, style="red")
            pc.print("\n Full Name : ", data.name, style="bright_cyan")
            pc.print("\n Bio : ", data.description, style="sandy_brown")
            pc.print("\n Url : ", data.url, style="aquamarine1")
            pc.print("\n Location : " ,data.location, style="orchid2")
            pc.print("\n Total Favourites Tweets : "  ,data.favourites_count, style="bright_yellow")
            pc.print("\n Followers :  ", data.followers_count, style='orange_red1')
            pc.print("\n Following : ", data.friends_count, style='orchid2')
            pc.print("\n Total Tweets : ", data.statuses_count,style='green')
            pc.print("\n Active lists ", data.listed_count, style='yellow')
            pc.print("\n Recent Tweet : {} at {}".format(data.status.text, data.status.created_at), style='gold1')
            pc.print("\n Active Device or Medium : {}".format(data.status.source), style="orchid1")
            print("\n Downloading target's profile picture...")
            try:
                URL = data.profile_image_url
                if URL != "":
                    end = "../../results/" + self.target + "_profile_pic.jpg"
                    urllib.request.urlretrieve(URL,end)
                    pc.print("Photos saved in results/ folder.", style="light_green")
                else:
                    pc.print("Sorry unable to download this time.", style="bright_red")
            except Exception as err:
                pc.print(err, style='red')
            
            print("\n Downloading banner of target's profile...") 
            try:
                URL = data.profile_banner_url
                if URL != "":
                    end = "../../results/" + self.target + "_banner.jpg" 
                    urllib.request.urlretrieve(URL, end)
                    pc.print("Banner is saved in results/ folder", style='light_green')
                
                else:
                    pc.print("Unable to download banner. Sorry!", style="red")
            except Exception as err:
                pc.print(err, style="red")
            
            pass
        
        except Exception as err:
            pc.print(err, style="bright_red")
            pass    
        
    
    def __setTarget__(self, target):
        target = self.target
        return target
        
    def reset_target(self):
        pc.print("Enter new Target's Screen Name : ")
        user_input = input()
        self.__setTarget__(user_input)
        return
        
      
    def total_fav(self):
        
        #total favourites of target
        fav = self.api.GetFavorites(screen_name=self.target)
        for f in fav:
            print(f)
        return
        
        
    def get_frnds(self):
        
        #get followings of target
        followings = self.api.GetFriends(screen_name=self.target)
        print(followings)  
        
    
    def get_followers(self):    
        
        #get followers of target
        followers = self.api.GetFollowers(screen_name=self.target)
        print(followers)
        
        
    def get_list(self):
        #let's try some function
        list = self.api.GetListMembers(slug='elon', owner_screen_name=self.target)
        print(list)
            
      
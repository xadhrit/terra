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
from rich.style import Style
import twitter
from rich.console import Console

pc = Console()


class Twitter:
    api = None
    api2 = None
    #eolocator = Nominatim(user_agent="http")
    #ser_id =None
    #tatus = None
    #riends = None
    target = ""
    #riteFile = False
    #sonDump = False

    def __init__(self, target,is_file, is_json):
    
        self.__setTarget__(target)
        pc.print("\nValidating Your Credentials...", style="cyan")
        self.__verifyCreds__()
        self.writeFile = is_file
        self.jsonFile = is_json
         
    
    def __verifyCreds__():
        data = []
         
        api = twitter.Api(consumer_key='7np6DuME8eguQJ1A0iYrefzaQ',consumer_secret='6AuPpib8uJGnKDdA9nJcDnnHWWajfNiqsHIxH5j6E7rXyrG9nZ',access_token_key='1291638708110651392-T00PIQffV3zCEB5VjPUo9Zi6ziCGdq',access_token_secret='fDraPtVcJ0SX71ncPPwiNINHsyzdlEsJNpwkFT2Gd6PbF')
        result = api.VerifyCredentials()
        data.extend(result.description)
        #print(data)
        return data
    #__verifyCreds__()
    
    def 
    
    def recent_tweets(self):
        name = input("Enter Screen Name of Target")
        tweets = self.api.GetUserTimeline(screen_name=name)
        for t in tweets:
            tt = t.text
            pc.print(tt, style="yellow")
        return    
    
    def __setTarget__(self, target):
        
    
        # recent recent tweets of target
        #statuses = api.GetUserTimeline(screen_name='xadhrit')
        #for s in statuses:
            #st = s.text
            #print(st)
        
        #total favourites of target
        #fav = api.GetFavorites(screen_name='xadhrit')
        #for f in fav:
            #print(f)
    
        #get followings of target
        #followings = api.GetFriends(screen_name='xadhrit')
        #print(followings)  
        
        #get followers of target
        #followers = api.GetFollowers(screen_name='xadhrit')
        #print(followers)1323481139537879042
        
        #get retweet via Status ID
        #info = api.GetRetweets(statusid='1323481139537879042') 
        #print(info)
            
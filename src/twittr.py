"""

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

pc = Console()


class Twitter:
    api = None
    api2 = None
    #eolocator = Nominatim(user_agent="http")
    #ser_id =None
    #tatus = None
    #riends = None
    #target = ""
    #riteFile = False
    #sonDump = False

    def __init__(self, target):
        u = self.__verifyCreds__()
        self.__chooseTarget__(target)

    def __verifyCreds__():
        api = twitter.Api(consumer_key='7np6DuME8eguQJ1A0iYrefzaQ',consumer_secret='6AuPpib8uJGnKDdA9nJcDnnHWWajfNiqsHIxH5j6E7rXyrG9nZ',access_token_key='1291638708110651392-T00PIQffV3zCEB5VjPUo9Zi6ziCGdq',access_token_secret='fDraPtVcJ0SX71ncPPwiNINHsyzdlEsJNpwkFT2Gd6PbF')
        verify = api.VerifyCredentials()
        #pc.print(verify, style="red")
        
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
            
    
    __verifyCreds__()

    

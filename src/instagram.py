import codecs
import datetime
import json
import requests
import sys
import urllib
import os
from rich.console import Console
from instagram_private_api import ClientCookieExpiredError, ClientLoginRequiredError,ClientError, ClientThrottledError
from instagram_private_api import Client as AppClient
from geopy.geocoders import Nominatim

pc = Console()

class Instagram:
    api=None
    api2=None
    geolocator=Nominatim(user_agent='http')
    user_id = None
    target_id = None
    is_private = True
    following = False
    target = ""
    writeFile = False
    jsonDump = False

    def __init__(self, target, is_file, is_json):
        user = self.__getUsername__()
        passwd = self.__getPassword__()
        pc.print("\nAttempting to Login ~~", style="green")
        self.login(user, passwd)
        self.setTarget(target)
        self.writeFile = is_file
        self.jsonDump = is_json

    def login(self, user, passwd):
        try:
            settings_file = "creds/settings.json"
            if not os.path.isfile(settings_file):
                #if file does not exit
                pc.print('Unable to find Settings file: {0!s}'.format(settins_file))

                #new login

                self.api = AppClient(auto_patch=True, authentication=True,username=user, password=passwd, on_login=lambda x: self.onlogin_callback(x, settings_file))

            else:
                with open(settings_file) as file_data:
                    cached_settings = json.load(file_data, object_hook=self.from_json) 

                    self.api = AppClient(
                            username=user, password=passwd,
                            settings=cached_settings,
                            on_login=lambda x: self.onlogin_callback(x, settings_file)
                            )

        except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
              pc.print("ClientCookieExpiredError/ClientLoginRequiredError {}".format(e), style="red")

              #login exired
              # login again
              self.api = AppClient(auto_patch=True, authentication=True, username=user, password=passwd, on_login=lambda x: self.on_login_callback(x, settings_file))




              







    def chooseTarget(self, target):
        self.target = target
        user = self.get_user(target)
        self.target_id = user['id']
        self.is_private = user['is_private']
        self.following = self.check_following()
        self.__printYourTarget__()


    def __getPassword__(self):
        try:
            passwd = open("creds/password.conf", "r").read()
            passwd = passwd.replace("\n", "")
            return passwd
        except FileNotFoundError:
            pc.print("Error: file not found", style="red")
            print("\n")
            sys.exit(0)


    def __getUsername__(self):
        try:
            user = open("creds/user.conf", "r").read()
            user = user.replace("\n", "")
            return user
        except FileNotFoundError:
            pc.print("Error: file not found", style="red")
            print("\n")
            sys.exit(0)


    def __getFeed__(self):
        data = []
        res = self.api.user_feed(str(self.target_id))
        data.extend(res.get("items", []))

        next_max_id = res.get('next_max_id')
        while next_max_id:
            results = self.api.user_feed(str(self.target_id),max_id=next_max_id )
            data.extend(results.get('items', []))
            next_max_id = results.get('next_max_id')

        return data

    def __getComments__(self, media_id):
        comments = []
        res = self.api.media_comments(str(media_id))
        comments.extend(res.get('comments', []))

        next_max_id = res.get('next_max_id')
        while next_max_id:
            results = self.api.media_comments(str(media_id), max_id=next_max_id)
            comments.extend(results.get("comments", []))
            next_max_id = results.get('next_max_id')

        return comments

    def __printTarget__(self):
        pc.print("\nLogged as", style="yellow")
        pc.print(self.api.username, style="green")
        pc.print(" Target: ", style="bold red")
        pc.print(str(self.target), style="white")
        pc.print(" [ " + str(self.target_id) + "]" )
        if self.is_private:
            pc.print("Target have Private Profile", style="hotpink")
        if self.following:
            pc.print("Following", style="orange")
        else:
            pc.print("You are not Following Target's Account ", style="red")


    def __getCaptions__(self):
        if self.check_private_profile():
            return
        
        pc.print("Filtering Target's Captions... \n", ":thumbs_up:")
        captions = []

        data = self.__getFeed__()
        num_of_captions = 0

        try:
            for item in data:
                if "caption" in item:
                    if item["caption"] is not None:
                        text = item["caption"]["text"]
                        captions.append(text)
                        sys.stdout.write("\rFound %i" % num_of_captions)
                        sys.stdout.flush()


        except AttributeError:
            pass
        except KeyError:
            pass
        # save results in json file
        caption_data = {}

        if num_of_captions > 0 :
            pc.print("\nFound " + str(num_of_captions) + "captions\n", style="cyan")

            
            if self.writeFile:
                file_name = "result/" + self.target + "_captions.txt"
                fCap = open(file_name, "w") 

            for s in captions:
                print(s + "\n")

                if self.writeFile:
                    fCap.write(s + "\n")

            if self.jsonDump:
                caption_data['captions'] = captions
                caption_file_name = "result/" + self.target + "_followings.json"
                with open(cpation_file_name, 'w') as f:
                    json.dump(caption_data, f)


            fCap.close()

        else:
            pc.print("Sorry! No Captions Found : \n", style="red")

        return


            

















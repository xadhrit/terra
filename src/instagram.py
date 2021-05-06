import codecs
import datetime
import json
import requests
import sys
import urllib
import os
# rich table is not working here
from prettytable import PrettyTable
from rich.console import Console
from instagram_private_api import ClientCookieExpiredError, ClientLoginRequiredError, ClientError, ClientThrottledError
from instagram_private_api import Client as AppClient
from geopy.geocoders import Nominatim

pc = Console()


class Instagram:
    api = None
    api2 = None
    geolocator = Nominatim(user_agent='http')
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
        self.chooseTarget(target)
        self.writeFile = is_file
        self.jsonDump = is_json
     
    def write_file(self, flag):
        if flag:
            pc.print("Write to file: ", style="white")
            pc.print("enabled", style="yellow")
            print("\n")
        else:
            pc.print("Write to file : ", style="yellow")
            pc.print("disabled", style="red")
            print("\n")
            
        self.writeFile = flag
        
    def json_dump(self, flag):
        if flag:
            pc.print("Export to Json: ", style="yellow")
            pc.print("enabled", style="yellow")
            print("\n")
        else:
            pc.print("Export to Json: ", style="white")
            pc.print("disabled", style="red")
            print("\n")
            
        self.jsonDump = flag

    def login(self, user, passwd):
        try:
            settings_file = "creds/settings.json"
            if not os.path.isfile(settings_file):
                # if file does not exit
                pc.print(
                    'Unable to find Settings file: {0!s}'.format(settings_file))

                # new login

                self.api = AppClient(auto_patch=True, authentication=True, username=user,password=passwd, on_login=lambda x: self.onlogin_callback(x, settings_file))

            else:
                with open(settings_file) as file_data:
                    cached_settings = json.load(file_data, object_hook=self.from_json)

                    self.api = AppClient(
                        username=user, password=passwd,
                        settings=cached_settings,
                        on_login=lambda x: self.onlogin_callback(
                            x, settings_file)
                    )

        except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
            pc.print("ClientCookieExpiredError/ClientLoginRequiredError {}".format(e), style="red")

            # login exired
            # login again
            self.api = AppClient(auto_patch=True, authentication=True, username=user,password=passwd, on_login=lambda x: self.on_login_callback(x, settings_file))
            
        except ClientError as err:
            e = json.loads(err.error_response)
            pc.print(e['message'], style="red")
            pc.print(err.msg, style="red")
            print("\n")
            if 'challenage' in e:
                print("Please follow link to complete the challange " + e['challange']['url'])
            exit(9)
            
    def to_json(self, python_object):
        if isinstance(python_object, bytes):
            return {'__class__' : 'bytes', '__value__': codecs.encode(python_object, 'base64').decode()}
        raise TypeError(repr(python_object) + 'could not change into json.')
    
    def from_json(self, json_object):
        if '__class__' in json_object and json_object['__class__'] == 'bytes':
            return codecs.decode(json_object['__value__'].encode(), 'base64')
        return json_object
    
    def onlogin_callback(self, api, new_settings_file):
        cache_settings = api.settings
        with open(new_settings_file, 'w') as resultfile:
            json.dump(cache_settings, resultfile, default=self.to_json)
            print("Result has been save in {}".format(new_settings_file))

    def get_user(self, username):
        try:
            content = self.api.username_info(username)
            if self.writeFile:
                file_name = "results/" + self.target + ".txt"
                fp = open(file_name, "w")
                fp.write(str(content['user']['pk']))
                fp.close()
                
            user = dict()
            user['id'] = content['user']['pk']
            user['is_private'] = content['user']['is_private']
        
            return user
        
        except ClientError as err:
            e = json.loads(err.error_response)  
            if 'message' in e:
                pc.print(e['message'], style="red")
            elif 'error_title' in e:
                pc.print(e['error_title'], style="red")
            elif 'challenge' in e:
                pc.print("Please follow this complete " + e['challenge']['url'])
                
            sys.exit(2)
    

    def chooseTarget(self, target):
        self.target = target
        user = self.get_user(target)
        self.target_id = user['id']
        self.is_private = user['is_private']
        self.following = self.check_following()
        self.__printTarget__()

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
            
    def check_following(self):
        if str(self.target_id) == self.api.authenticated_user_id:
            return True
        endpoint = 'users/{user_id!s}/full_detail_info/'.format(**{'user_id' : self.target_id})
        return self.api._call_api(endpoint)['user_detail']['user']['friendship_status']['following']
    
    def check_private_profile(self):
        if self.is_private and not self.following:
            pc.print("User got a private Account\n", style="red")
            pc.print("You can send a follow request.. Want me to send it for you!? [y/n] \n ")
            
            request = input()
            
            if request.lower() == "y":
                self.api.friendships_create(self.target_id)
                pc.print("Done!")
            return True
        return False
        
    def target_locations():
        if self.check_private_profile():
            return
        pc.print("Searching for pinned locations of target...\n")
        
        data = self.__getFeed__()
        locations = {}
        
        for post in data:
            if 'location' in post and post['location'] is not None:
                if 'latitude' in post['location'] and 'longitude' in post['location']:
                    lt = post['location']['latitude']
                    log = post['location']['longitude']
                    locations[str(lt) + ', ' + str(lng)] = post.get('online at')
                    
        post_location = {}
        for l, n in post_location.items():
            detail = self.geolocator.reverse(l)
            time = datetime.datetime.fromtimestamp(n)
            post_location[detail.post_location] = time.strftime('%Y-%m-%d %H:%M:%S')
            
        locations_sort = sorted(post_location.items(), key=lambda x: x[1], reverse=True)
        
        if len(locations_sort) > 0:
            t = PrettyTable()
            t.field_names = ['Post', 'Location', 'Time']
            t.align['Post'] = "l"
            t.align['Location'] = "l"
            t.align['Time'] = "l"
            pc.print("Results " + str(len(locations_sort)) + " addresses\n", style="cyan")
            
            data_in_json = {}
            locations_list = []
            
            for post_location, time in locations_sort:
                t.add_row([str(i), address, time]) 
                 
                if self.jsonDump:
                    loc = {
                        'Location':post_location,
                        'Time': time
                    }
                    locations_list.append(loc)
                    
            if self.writeFile:
                file_name = "results/"+ self.target + "_locations.txt"
                fp = open(file_name, "w")
                fp.write(str(t))
                fp.close()
                
            if self.jsonDump:
                data_in_json['post_location'] = locations_list
                file_name = "results/" + self.target + "_locations.json"
                with open(file_name, "w") as fp:
                    json.dump(data_in_json, fp)
                    
            print(t)
        else:
            pc.print("It seems like user haven't pinned any location until now.", style="red")
            
        
            
    
     
    def __getFeed__(self):
        data = []
        res = self.api.user_feed(str(self.target_id))
        data.extend(res.get("items", []))

        next_max_id = res.get('next_max_id')
        while next_max_id:
            results = self.api.user_feed(
                str(self.target_id), max_id=next_max_id)
            data.extend(results.get('items', []))
            next_max_id = results.get('next_max_id')

        return data

    def __getComments__(self, media_id):
        comments = []
        res = self.api.media_comments(str(media_id))
        comments.extend(res.get('comments', []))

        next_max_id = res.get('next_max_id')
        while next_max_id:
            results = self.api.media_comments(
                str(media_id), max_id=next_max_id)
            comments.extend(results.get("comments", []))
            next_max_id = results.get('next_max_id')

        return comments

    def __printTarget__(self):
        pc.print("\nLogged as", style="yellow")
        pc.print(self.api.username, style="green")
        pc.print(" Target: ", style="bold red")
        pc.print(str(self.target), style="white")
        pc.print(" [ " + str(self.target_id) + "]")
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

        if num_of_captions > 0:
            pc.print("\nFound " + str(num_of_captions) +
                     "captions\n", style="cyan")

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

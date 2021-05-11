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
            settings_file = "../../creds/settings.json"
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
                file_name = "../../results/" + self.target + ".txt"
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
        
    def change_target(self):
        pc.print("Choose a new target username: ", style="cyan")
        line = input()
        self.chooseTarget(line)
        return
        

    def __getPassword__(self):
        try:
            passwd = open("../../creds/password.conf", "r").read()
            passwd = passwd.replace("\n", "")
            return passwd
        except FileNotFoundError:
            pc.print("Error: file not found", style="red")
            print("\n")
            sys.exit(0)

    def __getUsername__(self):
        try:
            user = open("../../creds/user.conf", "r").read()
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
        
    def target_locations(self):
        if self.check_private_profile():
            return
        pc.print("Searching for pinned locations of target...\n")
        
        data = self.__getFeed__()
        #print(data)
        locations = {}
        
        
        for post in data:
            if 'location' in post and post['location'] is not None:
                if 'lat' in post['location'] and 'lng' in post['location']:
                    lat = post['location']['lat']
                    lng = post['location']['lng']
                    locations[str(lat) + ', ' + str(lng)] = post.get('taken_at')

        location = {}
        for k, v in locations.items():
            details = self.geolocator.reverse(k)
            unix_timestamp = datetime.datetime.fromtimestamp(v)
            location[details.address] = unix_timestamp.strftime('%Y-%m-%d %H:%M:%S')

        _locations = sorted(location.items(), key=lambda p: p[1], reverse=True)

        
        if len(_locations) > 0:
            t = PrettyTable()
            t.field_names = ['Post', 'Location', 'Time']
            t.align['Post'] = "l"
            t.align['Location'] = "l"
            t.align['Time'] = "l"
            pc.print("Results " + str(len(_locations)) + " locations\n", style="cyan")
        
            i = 1                
            
            data_in_json = {}
            locations_list = []
            
            for post_location, time in _locations:
                t.add_row([str(i), location , time]) 
                 
                if self.jsonDump:
                    loc = {
                        'Location':post_location,
                        'Time': time
                    }
                    locations_list.append(loc)
                
                i = i+1
                    
            if self.writeFile:
                file_name = "../../results"+ self.target + "_locations.txt"
                fp = open(file_name, "w")
                fp.write(str(t))
                fp.close()
                
            if self.jsonDump:
                data_in_json['post_location'] = locations_list
                file_name = "../../results/" + self.target + "_locations.json"
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
        pc.print("Logged as : ", style="yellow")
        pc.print(self.api.username, style="green")
        pc.print(". Target ", style="bold red")
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
                        num_of_captions= num_of_captions + 1
                        sys.stdout.write("\rFound %i  " %  num_of_captions)
                        sys.stdout.flush()

        except AttributeError:
            pass
        except KeyError:
            pass
        # save results in json file
        caption_data = {}
        #print(caption_data)

        if num_of_captions > 0:
            pc.print("\nFound " + str(num_of_captions) +
                     "captions\n", style="cyan")

            if self.writeFile:
                file_name = "../../result/" + self.target + "_captions.txt"
                fCap = open(file_name, "w")

            for s in captions:
                print(s + "\n")

                if self.writeFile:
                    fCap.write(s + "\n")

            if self.jsonDump:
                caption_data['captions'] = captions
                caption_file_name = "../../result/" + self.target + "_followings.json"
                with open(caption_file_name, 'w') as f:
                    json.dump(caption_data, f)
            
            
                    fCap.close()
            

        else:
            pc.print("Sorry! No Captions Found : \n", style="red")

        return
    
    def _all_comments(self):
        if self.check_private_profile():
            return
        pc.print("Searching for target's all comments...\n")
        
        comments_count = 0
        posts = 0
        data = self.__getFeed__()
        
        for post in data:
            comments_count += post['comment_count']
            posts += 1
            
        if self.writeFile:
            file_name = "../../results/" + self.target + "_comments.txt"
            fComments = open(file_name,"w")
            fComments.write(str(comments_count) + "comments in " + str(posts) + " posts\n")
            
        if self.jsonDump:
            json_data = {
                'comments_count':comments_count,
                'posts':posts
            }
            json_file_name = "../../results/" + self.target + "_comments.json"
            with open(json_file_name, 'w') as fp:
                json.dump(json_data,fp)
                
        pc.print(str(comments_count), style="magenta")
        pc.print("comments in " + str(posts) + " posts")
        
    def _followers(self):
        if self.check_private_profile():
            return
        pc.print("Searching for target's followers....\n", style="yellow")
        
        get_followers = []
        followers = []
        
        rank_token = AppClient.generate_uuid()
        data = self.api.user_followers(str(self.target_id), rank_token=rank_token)
        
        get_followers.extend(data.get('users', []))
        
        next_max_id = data.get('next_max_id')
        while next_max_id:
            sys.stdout.write("\rDiscovered %i followers" % len(get_followers))
            sys.stdout.flush()
            results = self.api.user_followers(str(self.target_id), rank_token=rank_token, max_id=next_max_id)
            get_followers.extend(results.get('users', []))
            next_max_id = results.get('next_max_id')
            
        print("\n")
        
        for user in get_followers:
            users = {
                'id': user['pk'],
                'username':user['username'],
                'full_name': user['full_name']
            }
            followers.append(users)
            
        t = PrettyTable(['ID', 'Username', 'Full Name'])
        t.align["ID"] = "l"
        t.align["Username"] = "l"
        t.align["Full Name"] = "l"
        
        json_data = {}
        followings_list = []
        
        for node in followers:
            t.add_row([str(node['id']), node['username'], node['full_name']])
            if self.jsonDump:
                follow = {
                    'id': node['id'],
                    'username' : node['username'],
                    'full_name': node['full_name']
                }
                followings_list.append(follow)
                
        if self.writeFile:
            file_name = "../../results/" + self.target + "_followers.txt"
            ffollowers = open(file_name, "w")
            ffollowers.write(str(t))
            ffollowers.close()
            
        if self.jsonDump:
            json_data['followers'] = followers
            json_file_name = "../../results/" + self.target + "_followers.json"
            with open(json_file_name, "w") as fp:
                json.dump(json_data, fp)
                
        print(t)
        
        
    def _followings(self):
        if self.check_private_profile():
            return
        
        pc.print("Searching for target's following....\n", style="cyan")
        
        get_followings = []
        followings = []
        
        rank_token = AppClient.generate_uuid()
        
        data = self.api.user_following(str(self.target_id), rank_token=rank_token)  
        get_followings.extend(data.get('users', [])) 
        
        next_max_id = data.get('next_max_id')
        while next_max_id:
            sys.stdout.write('\r Find %i followings' %len(get_followings))
            sys.stdout.flush()
            results = self.api.user_following(str(self.target_id), rank_token=rank_token, max_id=next_max_id)
            
            get_followings.extend(results.get('users', []))
            
            next_max_id  = results.get('next_max_id')
            
        print('\n')
        
        for user in get_followings:
            users  = {
                'id': user['pk'],
                'username': user['username'],
                'full_name' : user['full_name']
            }
            followings.append(users) 
            
        t =PrettyTable(['ID', 'Username', 'Full Name'])
        
        t.align["ID"] = "l"
        t.align["Username"] = "l"
        t.align["Full Name"] = "l"
        
        json_data = {}
        followings_list = []
        
        for node in followings:
            t.add_row([str(node['id']), node['username'], node['full_name']])
            
            if self.jsonDump:
                follow = {
                    'id': node['id'],
                    'username':node['username'],
                    'full_name':node['full_name']
                    
                }
                followings_list.append(follow)
                
        if self.writeFile:
            file_name = "../../results/" + self.target + "_followings.txt"
            ffollowings = open(file_name, "w")
            ffollowings.write(str(t))
            ffollowings.close()
            
        if self.jsonDump:
            json_data['followings'] = followings_list
            json_file_name = "../../results/" + self.target + "_followings.json"
            
            with open(json_file_name, "w") as fp:
                json.dump(json_data, fp)
                
        print(t)
        
    def _hashtags(self):
        if self.check_private_profile():
            return
        
        pc.print("Looking for target's used hahstags...\n", style="cyan")
        
        hashtags = []
        num_of_hashtags = 1
        texts = []
        
        data = self.api.user_feed(str(self.target_id))
        texts.extend(data.get('items', []))
        
        next_max_id = data.get('next_max_id')
        while next_max_id:
            results = self.api.user_feed(str(self.target_id), max_id=next_max_id)
            texts.extend(results.get('items', []))
            next_max_id = results.get('next_max_id')
            
        for post in texts:
            if post['caption'] is not None:
                caption = post['caption']['text']
                for tags in caption.split():
                    if tags.startswith('#'):
                        hashtags.append(tags.encode('UTF-8'))
                        num_of_hashtags += 1
                        
        if len(hashtags) > 0:
            hashtags_num = {}
            
            for h in hashtags:
                if h in hashtags_num:
                    hashtags_num[h] += 1
                else:
                    hashtags_num[h] = 1
                
            hashtags_ssort = sorted(hashtags_num.items(), key=lambda x:x[1], reverse=True)
        
            file = None
            json_data = {}
            hashtags_list = []
        
            if self.writeFile:
                file_name = "../../results/" + self.target + "_hashtags.txt"
                file  = open(file_name, "w") 
            
            for h,s in hashtags_ssort:
                hashtag = str(h.decode('utf-8'))
                print(str(s) + " . " + hashtag)
                if self.writeFile:
                    file.write(str(s) + " . " + hashtag)
                
                if self.jsonDump:
                    hashtags_list.append(hashtag)
                
            if file is not None:
                file.close()
            
            if self.jsonDump:
                json_data['hashtags'] = hashtags_list
                json_file_name = "../../results/" + self.target + "_hashtags.json"
                with open(json_file_name, "w") as fp:
                    json.dump(json_data, fp)
        
        else:
            pc.print("Sorry! We can not found any results.\n", style="red")                 
    
    def _user_timeline(self):
        try:
            endpoint = 'user/{user_id!s}/full_detail_info/'.format(**{'user_id':self.target_id})
            content = self.api._call_api(endpoint)
            #print(content)
            data = content['user_detail']['user']
            #print(data)
            
            pc.print("[ID]", style="green")
            print(str(data['pk']) + '\n')
            
            pc.print("[FULL NAME]", style="red")
            print(str(data['full_name']) + '\n')
            
            pc.print("[BIOGRAPHY]", style="cyan")
            print(str(data['biography']) + '\n')
            
            pc.print("[FOLLOWED]", style="red")
            print(str(data['follower_count']) + '\n')
            
            pc.print("[FOLLOW]", style="green")
            print(str(data['following_count']) + '\n')
   
            pc.print("[BUSINESS ACCOUNT]", style="red")
            print(str(data['is_business']) + '\n')
            
            
            if data['is_business']:
                if not data['can_hide_category']:
                    pc.print("BUSINESS CATEGORY", style="yellow")
                    print(str(data['category']) + '\n')
                    
            pc.print("[VERIFIED ACCOUNT]", style="cyan")
            print(str(data['is_verified']) + '\n')
            
            if 'public_email' in data and data['public_email']:
                pc.print("[EMAIL]", style="blue")
                print(str(data['public_email']) + '\n')
                
            pc.print("[ PROFILE PICTURE ]", style="green")
            print(str(data['hd_profile_pic_url_info']['url']) + '\n' )
            
            if 'fb_page_call_to_action_id' in data and data['fb_page_call_to_action_id']:
                pc.print("[Facebook Page]" , style="red")
                print(str(data['connected_fb_page']) + '\n')
                
            if 'whatsapp_number' in data and data['whatsapp_number']:
                pc.print("[What'sapp Number ]", style="yellow")
                print(str(data['whatsapp_number']) + '\n')
                
            if 'city_name' in data and data['city_name']:
                pc.print("[City Name]", style="green")
                print(str(data['city_name']) + '\n')
                
            if 'address_street' in data and data['address_street']:
                pc.print("[ Address Street ]", style="red")
                print(str(data['address_street']) +  '\n')
                
            if 'contact_phone_number' in data and data['contact_phone_number']:
                pc.print("[Contact Number]", style="green")
                print(str(data['contact_phone_number']) + '\n')
                
            if self.jsonDump:
                user = {
                    "id":data['pk'],
                    "full_name": data['full_name'],
                    'biography': data['biography'],
                    'edge_followed_by':data['follower_count'],
                    'edge_follow' :data['following_count'],
                    'is_business_account': data['is_business_account'],
                    'is_verified': data['is_business'],
                    'profile_pic_url_hd': data['hd_profile_pic_url_info']['url'],
                }
                if 'public_email' in data and data['public_email']:
                    user['email'] = data['public_email']
                        
                if 'fb_page_call_to_action_id' in data and data['fb_page_call_to_action_id']:
                    user['connected_fb_page'] = data['fb_page_call_to_action_id']
                        
                if 'whatsapp_number' in data and data['whatsapp_number']:
                    user['whatsapp_number']  = data['whatsapp_number']
                        
                if 'city_name' in data and data['city_name']:
                    user['city_name'] = data['city_name']
                        
                if 'address_street' in data and data['address_street']:
                    user['address_street'] = data['address_street']
                        
                if 'contact_phone_number' in data and data['contact_phone_number']:
                    user['contact_phone_number'] = data['contact_phone_number']
                        
                json_file_name = "../../results/" + self.target + "_info.json"
                with open(json_file_name, 'w') as fp:
                   json.dump(user, fp)
        
        except ClientError as err:
            pc.print(err, style="red") 
            print(str(self.target) + "not exist, please enter a valid username.")
            print('\n') 
            exit(2) 
            
    def _total_likes(self):
        if self.check_private_profile():
            return
        
        pc.print("Finding total likes of target....\n")
        
        like_num = 0
        posts = 0
        
        data = self.__getFeed__()
        
        for post in data:
            like_num += post['like_num']
            posts += 1
            
        if self.writeFile:
            file_name = "../../results/" + self.target + "_likes.txt"
            flikes = open(file_name, "w")
            flikes.write(str(like_num) + " likes in " + str(like_num) + "posts\n")
            flikes.close()
            
        if self.jsonDump:
            json_data = {
                'like_num': like_num,
                'posts': posts
            }
            json_file_name = "../../results/" + self.target +"_likes.json"
            with open(json_file_name , 'w') as fp:
                json.dump(json_data, fp)
                
        pc.print(str(like_num), style="magenta")
        pc.print(" likes in " + str(posts)+ " posts \n", style="yellow")
        
        
    def _media_type(self):
        if self.check_private_profile():
            return
        pc.print("Searching for target captions...\n")
        
        num = 0
        photo_num = 0
        video_num = 0
        
        data = self.__getFeed__()
        
        for post in data:
            if 'media_type' in post:
                if post['media_type'] == 1:
                    photo_num = photo_num + 1
                elif post['media_type'] == 2:
                    video_num = video_num + 1
                    
                num = num + 1
                sys.stdout.write("\r Checked %i" % num)
                sys.stdout.flush()
                
        sys.stdout.write(" posts") 
        sys.stdout.flush()
        
        if num > 0:
            
            if self.writeFile:
                file_name = "../../results/" + self.target + "_mediaformat.txt" 
                fmedia_type = open(file_name, "w")
                fmedia_type.write(str(photo_num) + " photos and " + str(video_num) + " video posted by target \n" ) 
                fmedia_type.close()
            pc.print("\nCatched " + str(photo_num) + "video posted by target\n", style="cyan")    
            
            if self.jsonDump:
                json_file_name = "../../results/" + self.target  + "_mediaformat.json"
                json_data = {
                    "photos"  :photo_num,
                    "videos" : video_num
                }
                with open(json_file_name, 'w') as fp:
                    json.dump(json_data, fp)
                    
        else:
            pc.print("No Results Found \n", style="red")
            
            
    def _people_who_commented(self):
        if self.check_private_profile():
            return
        
        pc.print("Searching for users who commented...\n", style="yellow")
        
        data =self.__getFeed__()
        
        users = []
        
        for post in data:
            comments = self.__getComments__(post['id'])
            
            for comment in comments:
                if not any(u['id'] == comment['user']['pk'] for u in users):
                    user = {
                        'id':comment['user']['pk'],
                        'username': comment['user']['username'],
                        'full_name': comment['user']['full_name'],
                        'number': 1
                    }
                    users.append(user)
                    
                else:
                    for user in users:
                        if user['id'] == comment['user']['pk']:
                            user['number'] += 1
                            break
                        
        if len(users) > 0 :
            ssorted = sorted(users, key=lambda y: y['number'], reverse=True)
            
            json_data = {}
            
            t = PrettyTable()
            
            t.field_names = ['Comments', 'ID', 'Username', 'Full Name']
            t.align["Comments"] = "l"
            t.align["ID"] ="l"
            t.align["Username"] = "l"
            t.align["Full Name"] = "l"
            
            for u in ssorted:
                t.add_row([str(u['number']), u['id'], u['username'], u['full_name']])
                
            print(t)
            
            if self.writeFile:
                file_name = "../../results/"+ self.target + "_users_who_commented.txt"
                fusers = open(file_name, "w")
                fusers.write(str(t))
                fusers.close()
                 
            if self.jsonDump:
                json_data['users_who_commented'] = ssorted
                json_file_name = "../../results/" + self.target + "_users_who_commented.json"
                with open(json_file_name, 'w') as fp:
                    json.dump(json_data, fp) 
                
                
        else:
            pc.print("No Users Found! \n", style="red")        
            
    def _users_who_tagged(self):
        if self.check_private_profile():
            return
        
        pc.print("Searching for Tagged Users..\n", style="yellow") 
        
        posts =[]
        result = self.api.usertag_feed(self.target_id)
        posts.extend(result.get('items', [])) 
        
        next_max_id = result.get('next_max_id')
        while next_max_id:
            results = self.api.user_feed(str(self.target_id), max_id=next_max_id)
            posts.extend(results.get('items', []))
            next_max_id = results.get('next_max_id')
            
        if len(posts) > 0:
            pc.print("\n Hurrah!! We got " + str(len(posts)) + "photos\n", style="green" )
            
            users = []
            
            for post in posts:
                if not any(u['id'] == post['user']['pk'] for u in users):
                    user = {
                        'id': post['user']['pk'],
                        'username': post['user'['username']],
                        'full_name': post['user']['full_name'],
                        'number': 1
                    }
                    users.append(user)
                    
                else:
                    for user in users:
                        if user['id'] == post['user']['pk']:
                            user['number'] += 1
                            break
                        
            tagged_sort = sorted(users, key=lambda y:y['number'], reverse=True)
            
            json_data = {}
            t=PrettyTable()
            
            t.field_names = ['Photos', 'ID', 'Username', 'Full Name']
            
            t.align['Photos'] = "l"
            t.align['ID'] = "l"
            t.align['Username'] = "l"
            t.align['Full Name'] = "l"
            
            for u in tagged_sort:
                t.add_row([str(u['number']), u['id'], u['username'], u['full_name']])
                
            print(t)
            
            if self.writeFile:
                file_name = "../../results/"+ self.target + "_tagged.txt"
                ftagged = open(file_name,"w")
                ftagged.close()
                
            if self.jsonDump:
                json_data['users_who_tagged'] = tagged_sort
                json_file_name = "../../results/" + self.target + "_tagged.json"
                with open(json_file_name, 'w') as fp:
                    json.dump(json_data, fp)
                    
        else:
            pc.print("No users found!", style="red")
            
    def _photo_description(self):
        if self.check_private_profile():
            return
        
        content = requests.get("https://www.instagram.com/"+ str(self.target)+ "/?__a=1")
        data = content.json()
        
        _photo_description = data['graphql']['user'] ['edge_owner_to_timeline_media']['edges']
        if len(_photo_description) > 0:
            pc.print("Searching for Results...\n",style="green")
            
            num_of_descrip = 1
            
            t = PrettyTable(['Photo', 'Description'])
            t.align["Photo"] = "l"
            t.align["Description"] = "l"
            
            json_data = {}
            description_list = []
            
            for d in _photo_description:
                node = d.get('node')
                desc = node.get('accessibility_caption')
                t.add_row([str(num_of_descrip), desc])
                
                if self.jsonDump:
                    description = {
                        'description': desc
                    }
                    description_list.append(description)
                num_of_descrip += 1
                
            if self.writeFile:
                file_name = "../../results/" + self.target + "_descritption.txt"
                fdesc = open(file_name, "w")
                fdesc.close()
                    
            if self.jsonDump:
                json_data['descriptions']  = description_list
                json_file_name = "../../results/"+ self.target + "_desc.json"
                with open(json_file_name, 'w') as fp:
                    json.dump(json_data, fp)
                    
            print(t)
            
        else:
            pc.print("No Description Found!\n", style="red")
            
    
    def _user_photo(self):
        if self.check_private_profile():
            return
        
        num = -1
        pc.print("No. of photos you want to download (by default we will try to download all photos) : ", style="yellow")
        user_input = input()
        
        try:
            if user_input == "":
                pc.print("Downloading all publicly avaible...\n")
            else:
                num = int(user_input)
                pc.print("Fetching.. " + user_input + " photos..\n", style="green")
                
                
        except ValueError: 
            pc.print("Wrong Value Entered\n", style="red")
            return
        
        data = []
        num_of_photos = 0
        
        results = self.api.user_feed(str(self.target_id))
        data.extend(results.get('items', []))
        
        next_max_id = results.get('next_max_id')
        while next_max_id:
            res = self.api.user_feed(str(self.target_id), max_id=next_max_id)
            data.extend(res.get('items', []))
            next_max_id = res.get('next_max_id')
            
        try:
            for photo in data:
                if num_of_photos == num:
                    break
                if "image_version2" in photo:
                    num_of_photos = num_of_photos + 1
                    url = photo["image_version2"]["candidates"][0]["url"]
                    photo_id = photo["id"]
                    response = "../../results/"+ self.target + "_" + photo_id + ".jpg"
                    
                    urllib.request.urlretrieve(url, response)
                    sys.stdout.write("\r Downloaded %i" %num_of_photos)
                    sys.stdout.flush()
                    
                else:
                    carousel = photo["carousel_media"]
                    for c in carousel:
                        if num_of_photos == num:
                            break
                        num_of_photos = num_of_photos + 1
                        url = c["image_version2"]["candidates"][0]["url"]
                        
                        photo_id = c["id"]
                        response = "../../results/" + self.target + "_" + photo_id+ ".jpg"
                        
                        urllib.request.urlretrieve(url, response)
                        sys.stdout.write("\r Downloaded %i" %num_of_photos)
                        sys.stdout.flush()
                        
        except AttributeError:
            pass
        except KeyError:
            pass
        
        sys.stdout.write(" photos")
        sys.stdout.flush()
        
        pc.print("\n Task Completed! " + str(num_of_photos) + " photos downloaded in results folder \n", style="green")
        
    
    def _user_profilepic(self):
        
        try:
            endpoint = 'users/{user_id!s}/full_detail_info/'.format(**{'user_id' : self.target_id})
            content = self.api._call_api(endpoint)
            
            data = content['user_detail']['user']
            
            if 'hd_profile_pic_url_info' in data:
                URL = data['hd_profile_pic_url_info']['url']
            
            else:
                profile_pics = len(data['hd_profile_pic_versions']) 
                
                URL = data['hd_profile_pic_versions'][profile_pics - 1]['url'] 
                
            if URL != "":
                res = "../../results/" + self.target + "_dp.jpg" 
                urllib.request.urlretrieve(URL, res)
                pc.print("Target;'s Profile Picture downloaded in results/ folder \n", style="green")
                
            else:
                pc.print("Unable to Download Profile Picture \n", style="red")
                
        except ClientError as err:
            e = json.loads(err.error_response)
            print(e['message'])
            print(e['error_title'])
            exit(2)
            
    def _user_stories(self) :
        if self.check_private_profile():
            return
        
        pc.print("Searching for target's Stories..\n")
        data = self.api.user_reel_media(str(self.target_id)) 
        
        num_of_stories = 0
        
        if data['items']  is not None:
            num_of_stories = data['media_count'] 
            for s in data['items'] :
                story_id = s["id"]  
                if s['media_type'] == 1:  #if photo in story
                    url = s['image_version2']['candidates'][0]['url']
                    res =  "../../results/" + self.target + "_"+ story_id + ".jpg"
                    urllib.request.urlretrieve(url, res)
                    
                elif s['media_type'] == 2: # if video
                    url = s['video_versions'][0]['url']
                    res = "../../results/" + self.target + "_" + story_id + ".mp4"
                    
                    urllib.request.urlretrieve(url, res)
                    
        if num_of_stories > 0:
            pc.print(str(num_of_stories) + " target stories saved in results folder\n", style="green")
            
        else:
            pc.print("No Story Found!", style="red")
            
            
    def _people_who_tagged_by_target(self):
        print("Searching for users tagged by target...\n")
        
        ids = []
        username =[]
        full_name = []
        post = []
        num_of_tusers = 1
        
        data = self.__getFeed__()
        
        try:
            for u in data:
                if 'usertags' in u:
                    user = u.get('usertags').get('in')
                    for ut in user:
                        if ut.get('user').get('pk') not in ids:
                            ids.append(ut.get('user').get('pk'))
                            username.append(ut.get('user').get('username'))
                            full_name.append(ut.get('user').get('full_name'))
                            post.append(1)
                        
                        else:
                            index = ids.index(ut.get('user').get('pk'))
                            post[index] += 1
                        num_of_tusers =  num_of_tusers + 1
                        
        except AttributeError as err:
            pc.print("\n Error: something went wrong", style="white")
            pc.print(err, style="red")
            print("")
            pass
        if len(ids) > 0:
            t = PrettyTable()
            t.field_names = ['Posts', 'Full Name','Username', 'ID']
            
            t.align["Posts"] = "l"
            t.align["Full Name"] = "l"
            t.align["Username"] = "l"
            t.align["ID"] = "l"
            
            pc.print("\n Discovered " + str(len(ids)) + " "  + str(num_of_tusers) + "users \n", style="green" )
            
            json_data  = {}
            tagged_list = []
            
            for i in range(len(ids)):
                t.add_row([post[i], full_name[i], username[i], str(ids)])
                
                if self.jsonDump:
                    tag = {
                        'post' : post[i],
                        'full name' : full_name[i],
                        'username'  : username[i],
                        'id': ids[i]
                    }
                    tagged_list.append(tag)
                    
            if self.writeFile:
                file_name = "../../results/" + self.target + "user_tagged.txt"
                fp = open(file_name, "w")
                fp.write(str(t))
                fp.close()
                
            if self.jsonDump:
                
                json_data['tagged'] = tagged_list
                json_file_name = "../../results/"+ self.target + "_tagged.json"
                
                with open(json_file_name, 'w') as fp:
                    json.dump(json_data, fp)
                    
            print(t)
            
        else:
            pc.print("No Users Found...\n", style="red")
            
    
    def followers_email(self):
        if self.check_private_profile():
            return
        followers = []
        
        try:
            pc.print("Searching for emails of target followers...process can take a few minutes\n", style="yellow")
            
            rank_token = AppClient.generate_uuid()
            data =self.api.user_followers(str(self.target_id), rank_token=rank_token)
            
            for user in data.get('users', []):
                u = {
                    'id': user['pk'],
                    'username': user['username'],
                    'full_name': user['full_name']
                }
                followers.append(u)
                
            next_max_id = data.get('next_max_id')  
            while next_max_id:
                sys.stdout.write("\r Discovered %i followers email" % len(followers)) 
                sys.stdout.flush()
                
                results = self.api.user_followers(str(self.target_id), rank_token=rank_token, max_id=next_max_id) 
                
                for user in results.get('users', []):
                    u = {
                      'id' : user['pk'],
                      'username': user['username']  ,
                      'full_name': user['full_name']  
                    }
                    followers.append(u)
                    
                next_max_id = results.get('next_max_id')
            print('\n')
            
            results = []
            
            for follow in followers:
                user = self.api.user_info(str(follow['id']))
                if 'public_email' in user['user'] and user['user']['public_email']:
                    follow['email'] = user['user']['public_email']
                    results.append(follow)
                    
        except ClientThrottledError as err:
            pc.print('\n Error: Instagram blocked the requests. Try again after some minutes...', style="red")
            
            print("\n")
            return
        if  len(results) > 0:
            t = PrettyTable(['ID', 'Username', 'Full Name', 'Email'])
            
            t.align["ID"] = "l"
            t.align["Username"] = "l"
            t.align["Full Name"] = "l"
            t.align["Email"] = "l"
            
            json_data = {}
            
            for node in results:
                t.add_row([str(node['id']), node['username'], node['full_name'], node['email']])
                
            if self.writeFile:
                file_name = "../../results/"+ self.target+ "_emails.txt"
                fp = open(file_name, "w")
                fp.write(str(t))
                fp.close()
                
            if self.jsonDump:
                json_data['followers_email'] = results
                json_file_name = "../../results/"+ self.target + "_emails.json"
                
                with open(json_file_name, "w") as fp:
                    json.dump(json_data, fp)
                    
            print(t)
        else:
            pc.print("No Emails Found...\n", style="red")
            
            
    def followings_email(self):
        if self.check_private_profile():
            return
        
        followings = []
        
        try:
            pc.print("Searching for emails of target's followings list...\n", style="white")
            rank_token = AppClient.generate_uuid()
            data = self.api.user_following(str(self.target_id), rank_token=rank_token) 
            
            for user in data.get('users', []) :
                u = {
                    'id' : user['pk'],
                    'username':user['username'],
                    'full_name': user['full_name']
                }
                followings.append(u)
                
            next_max_id = data.get('next_max_id')
            
            while next_max_id:
                results = self.api.user_following(str(self.target_id), rank_token=rank_token, max_id=next_max_id)
                
                for user in results.get('users', []):
                    u = {
                        'id':user['pk'],
                        'username':user['username'],
                        'full_name': user['full_name']
                    }
                    followings.append(u)
                    
                next_max_id =  results.get('next_max_id')
                
            results = []
            
            for u in followings:
                sys.stdout.write("\r Discovered %i followings eamil" % len(results))
                sys.stdout.flush()
                user = self.api.user_info(str(u['id']))
                
                if 'public_email' in user['user'] and user['user']['public_email']:
                    u['email'] = user['user']['public_email']
                    results.append(u)
        
        except ClientThrottledError as error:
            pc.print(error,style="red")
            return
            print("\n")
            
        print('\n')
        
        if len(results) > 0 :
            t = PrettyTable(['ID', 'Username', 'Full Name', 'Email'])
            t.align["ID"] = "l"
            t.align["Username"]  ="l"
            t.align["Full Namr"] = "l"
            t.align["Email"] ="l"
            
            json_data = {}
            
            for node in results:
                t.add_row([str(node['id']), node['username'], node['full_name'], node['email']])
                
                if self.writeFile:
                    file_name = "../../results/" + self.target + "followingsemail.txt"
                    fp  = open(file_name, "w")
                    fp.write(str(t))
                    fp.close()
                    
                if self.jsonDump:
                    json_data['followings_email'] = results
                    json_file_name = "../../results/"+ self.target + "_followingsemail.json"
                    with open(json_file_name, "w") as fp:
                        json.dump(json_data, fp)
                        
                print(t)
                
        else:
            pc.print("No Emails Found...\n", style="red")
            
    def followings_phoneNumber(self):
        if self.check_private_profile():
            return
        
        results = []
        
        try:
            pc.print("Searching for phone numbers of target's following... process can take few minutes\n", style="yellow")
            
            followings =[]
            rank_token = AppClient.generate_uuid()
            data = self.api.user_following(str(self.target_id), rank_token=rank_token)
            
            for user in data.get('users', []):
                u = {
                    'id' : user['pk'],
                    'username': user['username'],
                    'full_name': user['full_name']
                }
                followings.append(u)
                
            next_max_id = data.get('next_max_id')
            
            while next_max_id:
                results = self.api.user_followings(str(self.target_id), rank_token=rank_token, max_id=next_max_id)
                
                for user in results.get('users',[]):
                    u = {
                        'id': user['pk'],
                        'username':user['username'],
                        'full_name':user['full_name']
                    }
                    followings.append(u)
                    
                next_max_id = results.get('next_max_id')
                
            for follow in followings:
                sys.stdout.write("\r Discovered %i followings phone numbers " % len(results))
                sys.stdout.flush()
                user = self.api.user_info(str(follow['id']))
                
                if 'contact_phone_number' in user['user'] and user['user']['contact_phone_number']:
                    follow['contact_phone_number'] = user['user']['contact_phone_number']
                    results.append(follow)
                    
        except ClientThrottledError as err:
            pc.print("\n Error: Instagram Blocked your requests. Try again after few minutes...\n", style="red")
            print("\n")
            return
        
        print('\n')
        
        if len(results) > 0:
            t = PrettyTable(['ID', 'Username', 'Full Name', 'Phone'])
            t.align["ID"] = "l"
            t.align["Username"] = "l"
            t.align["Full Name"]= "l"
            t.align["Phone Number"] = "l"
            
            json_data = {}
            
            for node in results:
                t.add_row([str(node['id']), node['username'], node['full_name'],node['contact_phone_number']])
                
                if self.writeFile:
                    file_name = "../../results/" + self.target + "_followingsnumber.txt"
                    
                    fp = open(file_name, "w")
                    fp.write(str(t))
                    fp.close()
                if self.jsonDump:
                    json_data['followings_phone_numbers'] = results
                    json_file_name = "../../results/" + self.target + "_followingsnumber.json"
                    
                    with open(json_file_name, 'w')  as fp:
                        json.dump(json_data, fp)
                print(t)
        else:
            pc.print("No Phone Numbers Found", style="red")    
    
    def followers_phoneNumber(self):
        if self.check_private_profile():
            return
        
        followers  =[]
        
        try:
            pc.print("Searching for target's followers phone numbers....\n", style="yellow") 
            
            rank_token = AppClient.generate_uuid()
            data = self.api.user_followers(str(self.target_id), rank_token=rank_token) 
            
            for user in data.get('users', []) :
                u = {
                    'id': user['pk'],
                    'username': user['username'],
                    'full_name': user['full_name']
                }         
                followers.append(u)
                
            next_max_id = data.get('next_max_id')
            
            while next_max_id:
                results = self.api.user_followers(str(self.target_id), rank_token=rank_token, max_id=next_max_id)
                
                for user in results.get('users', []):
                    u  = {
                        'id': user['pk'],
                        'username': user['username'],
                        'full_name': user['full_name']
                        
                    }
                    followers.append(u)
                    
                next_max_id = results.get('next_max_id')
                
            results = []
            
            for follow in followers:
                sys.stdout.write("\r Discoverd %i followers phone numbers" % len(results))
                sys.stdout.flush()
                user = self.api.user_info(str(follow['id']))
                
                if 'contact_phone_number' in user['user'] and user['user']['contact_phone_number']:
                    follow['contact_phone_number'] = user['user']['contact_phone_number']
                    results.append(follow)
                    
        except ClientThrottledError as err:
            pc.print("\n Error: Instagram has blocked the requests. Try after few minutes.", style="red") 
            
            print("\n") 
            return
        print("\n")
        
        if len(results) > 0:
            t = PrettyTable(['ID', 'Username', 'Full Name', 'Phone'])
            t.align["ID"] = "l" 
            t.align["Username"] = "l"
            t.align["Full Name"] = "l"
            t.align["Phone Number"]  = "l" 
            
            json_data = {}
            
            for node in results:
                t.add_row([str(node['id']), node['username'], node['full_name'], node['contact_phone_number']]) 
                
            if self.writeFile:
                file_name = "../../results/" + self.target + "_followersnumber.txt"
                fp  =open(file_name, "w")
                fp.write(str(t))
                fp.close()
                
            if self.jsonDump:
                json_data['followers_phone_numbers'] = results
                json_file_name = "../../results/" +self.target + "_followersnumber.json"
                with open(json_file_name, fp):
                    json.load(json_data, fp) 
                    
            print(t)
        else:
            pc.print("No Numbers Found..\n", style="red")
            
    def _comments(self):
        if self.check_private_profile():
            return
        
        pc.print("Searching for users who commented on target's pics...\n", style="yellow")
        
        data = self.__getFeed__()
        commentUsers = []
        
        for  post in data:
            comments = self.__getComments__(post['id'])
            for comment in comments:
                print(comment['text'])
            
                     
                
        if len(commentUsers) > 0:
            cssort = sorted(commentUsers, key=lambda y:y['counter'], reverse=True)
            json_data = {}
            t = PrettyTable()
            
            t.field_names = ['Comments', 'ID', 'Username', 'Full Name']
            t.align['ID'] = "l"
            t.align["Comments"] = "l"
            t.align["Username"] = "l"
            t.align["Full Name"] = "l"
            
            for u in cssort:
                t.add_row([str(u['counter']), u['id'], u['username'], u['full_name']])
                
                print(t)
                
                if self.writeFile:
                    file_name = "../../results/"+ self.target + "_commenters.txt"
                    fp = open(file_name, "w")
                    fp.write(str(t))
                    fp.close()
                    
                if self.jsonDump:
                    json_data['user_who_commented'] = cssort
                    json_file_name = "../../results/"+ self.target + "commenters.json"
                    
                    with open(json_file_name, "w") as fp:
                        json.dump(json_data, fp)
                        
        else:
            pc.print("No Commenters Found! \n", style="red")
            
    
            
                             
            
                
    
        
                    
                    
                
                
            
    
                
                
                      
                           
            
              
        
        
            
                        
                        
                        
            
                         
        
                    
                    
                
                    
                    
                
                
            
            

        
                 
                
            
                    
        
        
        
        
         
                
                
                
        

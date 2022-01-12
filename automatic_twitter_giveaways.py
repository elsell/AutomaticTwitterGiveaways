import requests
import csv
from os import  path
import webbrowser
import datetime
import click
import json
import time
import random 
import configparser
import pytz

class AutomaticTwitterGiveaways:
    _REQUEST_TIMEOUT = 1.6
    _SHUFFLE_ITERATIONS = 10000

    _TWITTER_API_ENDPOINT = "https://api.twitter.com/2/"
    _TWITTER_API_TWEETS = "tweets/"
    _TWITTER_API_USERS = "users/"
    _TWITTER_API_SEARCH = "search/"
    _TWITTER_API_RETWEETS = "{}{}{}recent?query=retweets_of:{{user}}&start_time={{start_time}}&end_time={{end_time}}&max_results=100&expansions=author_id&tweet.fields=id,text,referenced_tweets&user.fields=username".format(_TWITTER_API_ENDPOINT,_TWITTER_API_TWEETS, _TWITTER_API_SEARCH)
    _TWITTER_API_FOLLOWERS = "{}{}{{user}}/followers?max_results=1000".format(_TWITTER_API_ENDPOINT, _TWITTER_API_USERS)
    _TWITTER_API_USER_INFO = "{}{}by/username/{{username}}".format(_TWITTER_API_ENDPOINT, _TWITTER_API_USERS)
    _TWITTER_API_COMMENTS = "{}{}{}recent?query=conversation_id:{{conversation_id}}%20has:hashtags%20%23{{hashtag}}&expansions=author_id&max_results=100&tweet.fields=id,text&user.fields=id,name,username".format(_TWITTER_API_ENDPOINT, _TWITTER_API_TWEETS,_TWITTER_API_SEARCH)

    def __init__(self, your_user_name: str,
                 giveaway_hashtag: str, 
                 giveaway_tweet_url: str,
                 bearer_token: str,
                 date_start: datetime.datetime,
                 date_end: datetime.datetime,
                 timezone_string: str,
                 output_to_csv: bool,
                 csv_output_filename: str,
                 debug=False):
        self._debug = debug

        self._user_name = your_user_name
        self._bearer_token = bearer_token
        self._giveaway_tweet_url = giveaway_tweet_url
        self._giveaway_hashtag = giveaway_hashtag
        self._giveaway_tweet_id = self._get_tweet_id_from_url(self._giveaway_tweet_url)
        self._user_id = self._get_userid_from_username(self._user_name)

        self._timezone_string = timezone_string

        self._date_start = self._local_time_to_utc(date_start)
        self._date_end = self._local_time_to_utc(date_end)

        self._output_to_csv = output_to_csv
        self._csv_output_filename = csv_output_filename

        spaces = 5
        width = 35
        print("Initializing AutomaticTwitterGiveaways:")
        print("{}{:<{width}}{}".format(" " * spaces, "Username:", self._user_name, width=width))
        print("{}{:<{width}}{}".format(" " * spaces, "UserID:", self._user_id, width=width))
        print("{}{:<{width}}{}".format(" " * spaces, "Giveaway Hashtag:", "#{}".format(self._giveaway_hashtag), width=width))
        print("{}{:<{width}}{}".format(" " * spaces, "Giveaway Tweet URL:", self._giveaway_tweet_url, width=width))
        print("{}{:<{width}}{}".format(" " * spaces, "Giveaway Tweet ID:", self._giveaway_tweet_id, width=width))
        print("{}{:<{width}}{}UTC".format(" " * spaces, "Giveaway Start Date:", self._date_start, width=width))
        print("{}{:<{width}}{}UTC".format(" " * spaces, "Giveaway End Date:", self._date_end, width=width))
        print("{}{:<{width}}{}".format(" " * spaces, "Output Followers & Retweets:", self._output_to_csv, width=width))
        if self._output_to_csv:
            print("{}{:<{width}}{}".format(" " * spaces, "Followers & Retweets Filename:", self._csv_output_filename, width=width))

        if self._debug:
            print("{}{:<{width}}{}".format(" " * spaces, "DEBUG:", self._debug, width=width))

        if len(self._bearer_token) == 0:
            print("\n[WARN] NO BEARER TOKEN FOUND!!! PLEASE CHECK THE CONFIGURATION FILE. ERRORS WILL PROBABLY FOLLOW THIS MESSAGE.\n")

    def _local_time_to_utc(self, time: datetime):
        local = pytz.timezone(self._timezone_string)
        local_dt = local.localize(time, is_dst=None)
        return local_dt.astimezone(pytz.utc)

    def _print_heading(self, message):
        print("-" * 80)
        print("{:^80}".format(message))
        print("-" * 80)

    def _clear_line(self):
        print(" " * 80, end="\r")

    def _get_request(self, url: str):
        if self._debug:
            print(url)
        r =  requests.get(url,headers={
            "Authorization": "Bearer {}".format(self._bearer_token)
        })

        data = json.loads(r.text)
        if 'errors' in data:
            if 'message' in data['errors'][0]:
                raise RuntimeError("[FAIL] There was a problem querying the Twitter API. Please see the message below for more information.\n\n{}".format(data['errors'][0]['message']))
        return r


    def _handle_request_error(self, status_code: int):
        if status_code == 429:
            raise RuntimeError("Too many requests have been made. Please wait 15 minutes and run again.")

    def _get_tweet_url_from_id_user(self, tweet_id:str, user_id:str):
        return "https://twitter.com/{}/status/{}".format(user_id, tweet_id)

    def _pick_random_winner(self, user_list: list): 
        # Shuffle, for good measure
        phrase = "Shuffling entries"
        for i in range(0, self._SHUFFLE_ITERATIONS):
            iter = i % 3
            suffix = "." * iter
            print("{}{}".format(phrase, suffix), end="\r")
            random.shuffle(user_list)
            self._clear_line()
        print("{}{}".format(phrase,"..."))

        return random.choice(user_list)

    def _get_tweet_id_from_url(self, url: str):
        # Remove last slash, if present
        if url[-1] == '/':
            url = url[:-1]

        tweet_id = url.split('/')[-1]

        # Check that it's the right length for a tweet id (this might change!!!)
        if not (18 <= len(tweet_id) <= 20):
            raise ValueError("Tweet ID '{}' does not seem to be a valid tweet ID. Please check the tweet URL and try again. Provided URL: {}".format(tweet_id, url))
        else:
            return tweet_id

    def _get_userid_from_username(self, username: str):
        request_url = self._TWITTER_API_USER_INFO.format(
            username=self._user_name
        )
        r = self._get_request(request_url)
        if r.status_code == 200:
            data = json.loads(r.text)["data"]
            user_id = data["id"]
            return user_id
        else:
            print("Failed to get user information: {}".format(r.status_code))
            self._handle_request_error(r.status_code)
            return None

    def _get_retweets(self, start_date: datetime.datetime, end_date: datetime.datetime):
        request_url = self._TWITTER_API_RETWEETS.format(
            user=self._user_name,
            start_time=start_date.isoformat().replace('+00:00', 'Z'),
            end_time=end_date.isoformat().replace('+00:00', 'Z')
        )
        r = self._get_request(request_url)

        data = json.loads(r.text)
        if r.status_code == 200 and 'data' in data:
            tweets = []
            tweet_data = data["data"]
            user_data = data["includes"]["users"]

            for tweet in tweet_data:
                author_id = tweet["author_id"]
                user_info = [u for u in user_data if u["id"] == author_id][0]
                referenced_tweets = tweet["referenced_tweets"]
                
                is_valid_retweet = False
                if referenced_tweets and len([t for t in referenced_tweets if t["id"] == self._giveaway_tweet_id]):
                    is_valid_retweet = True

                if is_valid_retweet:
                    tweets.append({
                        "tweet_id": tweet["id"],
                        "tweet_text": tweet["text"],
                        "author_username": user_info["username"],
                        "tweet_url": self._get_tweet_url_from_id_user(tweet["id"], user_info["id"]),
                        "author_displayname": user_info["name"],
                        "author_id": user_info["id"]
                    })
            
            while("next_token" in data["meta"]):
                print("Found {} re-tweets...".format(len(tweets)), end="\r")
                time.sleep(self._REQUEST_TIMEOUT)
                r =  self._get_request("{}&next_token={}".format(request_url, data["meta"]["next_token"]))

                if r.status_code == 200: 
                    data = json.loads(r.text)
                    tweet_data = data["data"]
                    user_data += data["includes"]["users"]

                    for tweet in tweet_data:
                        author_id = tweet["author_id"]
                        user_info = [u for u in user_data if u["id"] == author_id][0]

                        referenced_tweets = tweet["referenced_tweets"]
                        
                        is_valid_retweet = False
                        if referenced_tweets and len([t for t in referenced_tweets if t["id"] == self._giveaway_tweet_id]):
                            is_valid_retweet = True

                        if is_valid_retweet:
                            tweets.append({
                                "tweet_id": tweet["id"],
                                "tweet_text": tweet["text"],
                                "author_username": user_info["username"],
                                "tweet_url": self._get_tweet_url_from_id_user(tweet["id"], user_info["id"]),
                                "author_displayname": user_info["name"],
                                "author_id": user_info["id"]
                            })
                else:
                    print("Failed to make request: {}".format(r.status_code))
                    self._handle_request_error(r.status_code)
                    data["meta"] = {}

            return tweets

    def _get_followers(self):
        followers = []

        request_url = self._TWITTER_API_FOLLOWERS.format(
            user=self._user_id
        )
        r = self._get_request(request_url)

        data = json.loads(r.text)
        if r.status_code == 200 and 'data' in data: 
            follower_data = data["data"]

            # Get first line of data
            for follower in follower_data:
                followers.append({
                    "username": follower["username"],
                    "displayname": follower["name"],
                    "id": follower["id"],
                })

            # Get additional followers until we're done
            while "next_token" in data["meta"]:
                print("Found {} followers...".format(len(followers)),end="\r")
                time.sleep(self._REQUEST_TIMEOUT)
                next_token = data["meta"]["next_token"]
                request_url = self._TWITTER_API_FOLLOWERS.format(
                    user=self._user_id
                ) + "?pagination_token={}".format(next_token)
                r = self._get_request(request_url)

                if r.status_code == 200: 
                    data = json.loads(r.text)
                    follower_data = data["data"]

                    for follower in follower_data:
                        followers.append({
                            "username": follower["username"],
                            "displayname": follower["name"],
                            "id": follower["id"],
                        })  
                else:
                    print("Failed to get followers: {}".format(r.status_code))   
                    self._handle_request_error(r.status_code)           
                    data["meta"] = {}
        else:
            print("Failed to get followers: {}".format(r.status_code))
            self._handle_request_error(r.status_code)

        return followers

    def _get_replies(self, with_hashtag: str):
        replies = []

        request_url = self._TWITTER_API_COMMENTS.format(
            conversation_id=self._giveaway_tweet_id,
            hashtag=with_hashtag
        )
        r = self._get_request(request_url)

        # First page data
        data = json.loads(r.text)
        if r.status_code == 200 and 'data' in data:
            tweet_data = data["data"]
            user_data = data["includes"]["users"]

            for tweet in tweet_data:
                author_id = tweet["author_id"]
                user_info = [u for u in user_data if u["id"] == author_id][0]   

                replies.append({
                    "tweet_id": tweet["id"],
                    "tweet_text": tweet["text"],
                    "tweet_url": self._get_tweet_url_from_id_user(tweet["id"], user_info["id"]),
                    "user_id": user_info["id"],
                    "username": user_info["username"],
                    "displayname": user_info["name"],
                })

            # Second -> n page data
            while "next_token" in data["meta"]:
                print("Found {} #{} tweet comments...".format(len(replies), with_hashtag),end="\r")
                time.sleep(self._REQUEST_TIMEOUT)

                next_token = data["meta"]["next_token"]

                request_url = self._TWITTER_API_COMMENTS.format(
                    conversation_id=self._giveaway_tweet_id,
                    hashtag=with_hashtag
                ) + "&next_token={}".format(next_token)

                r = self._get_request(request_url)

                # First page data
                data = json.loads(r.text)
                if r.status_code == 200 and 'data' in data:
                    tweet_data = data["data"]
                    user_data = data["includes"]["users"]

                    for tweet in tweet_data:
                        author_id = tweet["author_id"]
                        user_info = [u for u in user_data if u["id"] == author_id][0]   

                        replies.append({
                            "tweet_id": tweet["id"],
                            "tweet_text": tweet["text"],
                            "tweet_url": self._get_tweet_url_from_id_user(tweet["id"], user_info["id"]),
                            "user_id": user_info["id"],
                            "username": user_info["username"],
                            "displayname": user_info["name"],
                        })

                else:
                    print("Failed to get more replies: {}".format(r.status_code))
                    self._handle_request_error(r.status_code)
                    data["meta"] = {}


        else:
            print("Failed to get replies: {}".format(r.status_code))
            self._handle_request_error(r.status_code)

        return replies

    def _print_retweet_and_follow(self, user_actions: dict):
        qualified_users = []

        for user in user_actions:
            user = user_actions[user]
            
            qualified = len(user["retweets"]) > 0 and len(user["follow"]) > 0

            if qualified:
                qualified_users.append(user)

        
        headers = ('Name', 'Username')
        with open(self._csv_output_filename, 'w', encoding="UTF-8") as file:
            csvwriter = csv.writer(file,delimiter=',', lineterminator='\n')
            csvwriter.writerow(headers)
            
            for user in qualified_users:
                csvwriter.writerow((user["follow"][0]["displayname"],
                                    user["follow"][0]["username"]))



    def pick_winner(self):

        self._print_heading("Retrieving Retweets")
        retweets = self._get_retweets(self._date_start, self._date_end)
        self._clear_line()
        print("Found {} Retweets.".format(len(retweets)))

        self._print_heading("Retrieving Comments")
        comments = self._get_replies(self._giveaway_hashtag)
        self._clear_line()
        print("Found {} #{} Comments.".format(len(comments), self._giveaway_hashtag))

        self._print_heading("Retrieving Followers")
        followers = self._get_followers()
        self._clear_line()
        print("Found {} Followers.".format(len(followers)))

        user_actions = {}

        # Catalog actions by user

        # RETWEETS
        for retweet in retweets:
            user_id = retweet["author_id"]
            if user_id not in user_actions:
                user_actions[user_id] = {
                    "retweets": [],
                    "follow": [],
                    "comments": []
                }
            user_actions[user_id]["retweets"].append(retweet)


        # FOLLOWS
        for follow in followers:
            user_id = follow["id"]
            if user_id not in user_actions:
                user_actions[user_id] = {
                    "retweets": [],
                    "follow": [],
                    "comments": []
                }
            user_actions[user_id]["follow"].append(follow)


        # COMMENTS
        for comment in comments:
            user_id = comment["user_id"]
            if user_id not in user_actions:
                user_actions[user_id] = {
                    "retweets": [],
                    "follow": [],
                    "comments": []
                }
            user_actions[user_id]["comments"].append(comment)

        if self._output_to_csv:
            self._print_heading("Printing Name/Username List")
            self._print_retweet_and_follow(user_actions)
            print("Done.")


        self._print_heading("Finding qualified users...")
        qualified_users = []
        

        for user in user_actions:
            user = user_actions[user]
            print("{} Qualified Users...".format(len(qualified_users)), end="\r")
            is_valid = len(user["retweets"]) > 0 and \
                       len(user["follow"]) > 0 and \
                       len(user["comments"]) > 0
            if is_valid:
                qualified_users.append(user)

        self._clear_line()
        print("Found {} Qualified Users.".format(len(qualified_users)))

        if len(qualified_users) > 0:

            self._print_heading("Picking Winner")
            winner = self._pick_random_winner(qualified_users)
            self._clear_line()
            self._print_heading("Winner Found!")
            print("\n\n{}\n\n".format(":)"*40))
            print("{:<30}{}".format("Name:", winner['follow'][0]['displayname']))
            print("{:<30}{}".format("Username:", winner['follow'][0]['username']))
            print("{:<30}{}".format("Comment URL:", winner['comments'][0]['tweet_url']))
            print("\n\n{}\n\n".format(":)"*40))

            return winner

        else:
           print("No qualified entries. Aborting.")
           return None


def get_config_param(config: configparser.RawConfigParser, section, key, is_boolean=False):
    if section in config:
        conf_sec = config[section]
        if key in conf_sec:
            if is_boolean:
                return config.getboolean(section, key)
            return config.get(section, key)
        else:
            raise RuntimeError("Key '{}' under section '{}' is required and missing from the configuration file.".format(key, section))
    else:
        raise RuntimeError("Section '{}' is required and was not found in the configuration file.".format(section))

if __name__ == "__main__":
    config_file_name = 'twitter_giveaway_config.ini'

    if not path.isfile(config_file_name):
        print("Please ensure file: {} is located in the same directory as this file.".format(config_file_name))
        click.pause("\n\nPress any key to exit...")

        raise SystemExit("Please ensure file: {} is located in the same directory as this file.".format(config_file_name))

    config = configparser.RawConfigParser()
    config.read(config_file_name)

    
    twitter_username = None
    giveaway_tweet_url = None
    giveaway_hashtag = None
    bearer_token = None

    date_start = None
    date_end = None
    timezone_string = None

    output_retweets_to_csv = None
    csv_output_name = None

    debug = False

    try:
        twitter_username = get_config_param(config, 'TwitterAuthentication','TwitterUsername')
        bearer_token = get_config_param(config, 'TwitterAuthentication','BearerToken')

        giveaway_tweet_url = get_config_param(config, 'GiveawayDetails','GiveawayTweetURL')
        giveaway_hashtag = get_config_param(config, 'GiveawayDetails','GiveawayTweetHashtag')

        yearStart = get_config_param(config, 'GiveawayDetails','GiveawayStartYear')
        monthStart = get_config_param(config, 'GiveawayDetails','GiveawayStartMonth')
        dayStart = get_config_param(config, 'GiveawayDetails','GiveawayStartDay')
        hourStart = get_config_param(config, 'GiveawayDetails', 'GiveawayStartHour')
        minuteStart = get_config_param(config, 'GiveawayDetails', 'GiveawayStartMinute')
        date_start = datetime.datetime(
            int(yearStart),
            int(monthStart),
            int(dayStart),
            int(hourStart),
            int(minuteStart))

        yearEnd = get_config_param(config, 'GiveawayDetails','GiveawayEndYear')
        monthEnd = get_config_param(config, 'GiveawayDetails','GiveawayEndMonth')
        dayEnd = get_config_param(config, 'GiveawayDetails','GiveawayEndDay')
        hourEnd = get_config_param(config, 'GiveawayDetails', 'GiveawayEndHour')
        minuteEnd = get_config_param(config, 'GiveawayDetails', 'GiveawayEndMinute')
        date_end = datetime.datetime(
            int(yearEnd),
            int(monthEnd),
            int(dayEnd),
            int(hourEnd),
            int(minuteEnd))
        timezone_string = get_config_param(config, "GiveawayDetails", "GiveawayTimezone")

        output_retweets_to_csv = get_config_param(config, "ListOutput", "OutputRetweetsAndFollows", True)
        csv_output_name = get_config_param(config, "ListOutput", "OutputFileName")

        debug = get_config_param(config, 'DEBUG', 'Debug', True)

    except RuntimeError as e:
        raise SystemExit("\n[FAIL] {}\n".format(str(e)))

    t = AutomaticTwitterGiveaways(twitter_username,
                        giveaway_hashtag,
                        giveaway_tweet_url,
                        bearer_token,
                        date_start,
                        date_end,
                        timezone_string,
                        output_retweets_to_csv,
                        csv_output_name,
                        debug)

    winner = None
    try:
        winner = t.pick_winner()
    except Exception as e:
        print("[FAIL] Could not pick winner: \n{}".format(str(e)))
        

    if winner:
        if click.confirm("Would you like to write this information to winner.json?", default=True):
            output_path = "winner.json"
            with open(output_path, 'w') as output_file:
                output_file.write(json.dumps(winner, indent=2))
            print("Winner written to: {}".format(output_path))
            webbrowser.open(output_path)

    click.pause("\n\nPress any key to exit...")
    

    
    


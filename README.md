# 🎁 AutomaticTwitterGiveaways 🎁
### AutomaticTwitterGiveaways automates selecting winners for "Retweet, Comment, Follow" type Twitter giveaways. 


## Contents
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Developer Notes](#developer-notes)
    - [Having issues?](#having-issues)
    - [Are you a student?](#if-youre-a-student)

## Quick Start
**Choose from one of these two options:**
 
### 1. Download a pre-built Executable
*This method does not require installing any dependencies*

1. [Download the Latest Release](https://github.com/elsell/AutomaticTwitterGiveaways/releases)
2. Extract the files.
3. Modify `twitter_giveaway_config.ini` to suit your needs (See [Configuration](#configuration))
4. Double-click on `Run Twitter Giveaway.exe`!

### 2. Run with Python
> *This method requires that [Python](https://www.python.org/downloads/) be installed.*

1. **Clone this repo**
```
git clone https://github.com/elsell/AutomaticTwitterGiveaways
```
2. **Navigate to project root directory** 
```
cd AutomaticTwitterGiveaways
```
3. **Install Dependencies**
```
python -m pip install -r requirements.txt
```
4. **Modify `twitter_giveaway_config.ini` to suit your needs (See [Configuration](#configuration))**

5. **Run the script**
```
python ./automatic_twitter_giveaways.py
```


## Configuration
> **Important:** A file named `twitter_giveaway_config.ini` must exist in the same directory as the script. 

Below is an example configuration file. Please note that to run AutomaticTwitterGiveaways, you must have a [Bearer Token](https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens) that you can get 
by [registering for a Twitter developer account (free)](https://developer.twitter.com/en/portal/petition/essential/basic-info).
```ini
;twitter_giveaway_config.ini

[TwitterAuthentication]
; Your Twitter Username
TwitterUsername=elonmusk
; Developer API Bearer Token
; Get one here:
; https://developer.twitter.com/en/portal/petition/essential/basic-info
BearerToken=

[GiveawayDetails]
; The URL of the tweet asking for retweets, comments, follows
GiveawayTweetURL=https://twitter.com/StubzNFT/status/1478720942981500939
; A hashtag required to make a comment valid
; (Omit the #. Ex. #NFT should be entered NFT)
GiveawayTweetHashtag=NFT

; Your timezone. Must be a valid TZ database name.
; A list of valid timezone strings can be found on Wikipedia:
; https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List
GiveawayTimezone=America/Chicago

; Start date/time of the giveaway (usually the time of the first tweet)
; The start date/time must be NO MORE than 7 days prior. 
; This is a limitation of the Twitter API, unfortunately. 
GiveawayStartYear=2022
GiveawayStartMonth=1
GiveawayStartDay=5

; Specify the hour in 24hr time. 
; Ex. 1PM => 13
GiveawayStartHour=16
GiveawayStartMinute=0


; End date/time of the giveaway
GiveawayEndYear=2022
GiveawayEndMonth=1
GiveawayEndDay=10

; Specify the hour in 24hr time. 
; Ex. 1PM => 13
GiveawayEndHour=0
GiveawayEndMinute=00

[ListOutput]
; Output a CSV list of name,username for each user that both 
; retweeted GiveawayTweetURL and follows TwitterUsername
OutputRetweetsAndFollows=True
; The name of the file to which to write the above-mentioned data. 
OutputFileName=followsAndRetweets.csv

[DEBUG]
; Display debug information, such as API request URLs
Debug=False
```


---------------------

## Developer Notes
First and foremost, I acknowledge that this tool has a pretty narrow
use-case. It was designed and built to solve a specific problem for 
a specific user. 

However, I have done my best to design it such that others may find some
use in it. If you have a use-case that is slightly different, and have
Python experience, please fork this repo and modify as needed!

> I will keep a list of all current (functionally-additive) forks and their use-cases in this repo. 


### Having issues?
Please [create an issue](https://github.com/elsell/AutomaticTwitterGiveaways/issues/)! I don't provide any warranty with this 
software, but I will be happy to give your issue a look. It also helps others
who may be looking to use this software determine if it is a good fit for them 🙂

### If you're a student
There is some messy code in here! Code duplication is through 
the roof at some points. There are better, more Pythontic ways to
do what this does. 

So if this bothers you AND you have time to do something about it,
please use this repo as an opportunity to delve into the open-source world!
Fork, make some changes, and submit a pull-request. 

The project is relatively small and would be a great introduction
to contributing to the FOSS world :)

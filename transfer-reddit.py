# Copies Reddit account subscriptions and r/all filters to a new account.  
# Launch and browser to http://localhost:8080

# pip install flask praw
from flask import Flask, render_template, redirect, request
import praw

app = Flask(__name__)

# You'll have to create a reddit app by visiting reddit.com/prefs/app
REDDIT_CLIENT_ID = 'XXXXXXXXXXXXXXXXXXXXXX'
REDDIT_CLIENT_SECRET = 'XXXXXXXXXXXXXXXXXXXXXX'
USER_AGENT = "something unique to you"


reddit = praw.Reddit(client_id= REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     redirect_uri='http://localhost:8080/callback',
                     user_agent=USER_AGENT)
login_url = reddit.auth.url(['*'], '...', 'permanent')

BASE_FILTERS = []
BASE_SUBS = []


@app.route("/")
def main():
    return render_template("main.html", url=login_url)


@app.route("/callback")
def callback():
    code = request.args.get("code")

    if len(BASE_FILTERS) == 0:
        reddit.auth.authorize(code)
        print(reddit.user.me())
        for fil in reddit.subreddit('all').filters:
            BASE_FILTERS.append(fil.display_name)

        for sub in reddit.user.subreddits(limit=None):
            BASE_SUBS.append(sub.display_name)

        global reddit2
        reddit2 = praw.Reddit(client_id= REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     redirect_uri='http://localhost:8080/callback',
                     user_agent=USER_AGENT)
                     
        login_url = reddit.auth.url(['*'], '...', 'permanent')

        login_url2 = reddit2.auth.url(['*'], '...', 'permanent')

        return render_template("second.html", url=login_url2)

    else:
        reddit2.auth.authorize(code)
        print(reddit2.user.me())

        print("removing subscribed subreddits")
        new_subreddits = list([sub.display_name for sub in reddit2.user.subreddits(limit=None)])
        print(new_subreddits)
        if new_subreddits:
            reddit2.subreddit(new_subreddits[0]).unsubscribe(other_subreddits=new_subreddits[1:])

        print("subscribing to base user")
        if BASE_SUBS:
            reddit2.subreddit(BASE_SUBS[0]).subscribe(other_subreddits=BASE_SUBS[1:])

        print("removing filters")
        try:
            for fil in reddit2.subreddit('all').filters:
                reddit2.subreddit('all').filters.remove(fil.display_name)
        except:
            print("error removing filters")

        print("adding r/all filters")
        for base_fil in BASE_FILTERS:
            reddit2.subreddit('all').filters.add(base_fil)
        return "It worked!"


if __name__ == "__main__":
    app.run(port=8080)

# TODO
    # Make sure to consider nicknames for all heroes
    # Make sure to credit idiap.ch rsearch institute for their positive and negative words

# Goal: Pull text data from Reddit on the Overwatch subreddit. Store data in local MySQL database.

# Manage imports
import mysql.connector
import praw
import datetime
import requests
from bs4 import BeautifulSoup

# Connects to local mysql db
# Returns the db instance
def db_connect():
    conn = mysql.connector.connect(
        user='root',
        password='root',
        host='localhost',
        database='dbo'
    )

    return conn

def pull_data_heroes(connection):
    pass

# Pull post and comment data from reddit
# Write data to local mysql database table - RedditPos, RedditComment
def pull_data_reddit(connection, hero_list, comment_count=25):
    cursor = connection.cursor()

    # Open db file log
    db_log = open("../logs/db_log.txt","a")

    r = praw.Reddit(user_agent="User-Agent: Overwatch Reddit Sentiment Analysis 1.0 by /u/dalisaydavid")
    submissions = r.get_subreddit('Overwatch').get_top(show='all',limit=None)

    post_list = []
    total_posts = 0
    total_comments = 0
    for submission in submissions:
        post = submission.title.lower()
        if '\'' in post or '\"' in post:
            if '\'' in post:
                post = post.replace('\'', '\\\'')
            if '\"' in post:
                post = post.replace("\"", "\\\"")
        elif '\\' in post:
            post = post.replace("\\","\\\\")

        # If the title doesn't have a Hero name... don't use it.
        hero_ref = None
        for hero in hero_list:
            hero_name = hero[1]
            if hero_name in post:
                hero_ref = hero[0]
                break
        if not hero_ref:
            continue

        author = submission.author
        date_time = datetime.datetime.fromtimestamp(int(submission.created_utc)).strftime('%Y-%m-%d %H:%M:%S')
        upvotes = submission.ups

        # Insert the Reddit Post
        post_insert_str = "INSERT INTO RedditPost (hero_ref_id,post,author,enddate,upvotes) VALUES (%i, '%s', '%s', '%s',%i)" % (hero_ref,post,author,date_time,upvotes)
        print("post_insert_str: %s" % post_insert_str)
        add_reddit_post = (post_insert_str)
        cursor.execute(add_reddit_post)
        #connection.commit()

        # Remember the post id
        post_id = cursor.lastrowid

        total_posts += 1

        # Log db write
        db_log.write("%s ### %i Posts checked. Written to RedditPost table.\n" % (datetime.datetime.now(),total_posts))

        comment_index = 0
        for comment in submission.comments:
            if comment_index == comment_count:
                print("#### Comment Count %i Exceeded ####" % (comment_count))
                break
            # If the comment doesn't have a Hero name... don't use it.
            # NOTE: The hero_ref_id in comment can be different than hero_ref_id in main post.
            # Check for quotes...
            if 'body' not in vars(comment):
                continue
            body_c = comment.body.lower()
            if '\'' in body_c or '\"' in body_c:
                if '\'' in body_c:
                    body_c = body_c.replace('\'', '\\\'')
                if '\"' in body_c:
                    body_c = body_c.replace("\"", "\\\"")
            elif '\\' in body_c:
                body_c = body_c.replace("\\","\\\\")

            author_c = comment.author
            date_time_c = datetime.datetime.fromtimestamp(int(comment.created_utc)).strftime('%Y-%m-%d %H:%M:%S')
            upvotes = comment.ups

            hero_ref_c = None
            for hero in hero_list:
                hero_name = hero[1]
                if hero_name in body_c:
                    hero_ref_c = hero[0]
                    break
            if not hero_ref_c:
                continue

            # Insert Reddit Comment
            comment_insert_str = "INSERT INTO RedditComment (comment,author,enddate,upvotes,post_id,hero_ref_id) VALUES ('%s', '%s', '%s',%i, %i, %i)" % (body_c,author_c,date_time_c,upvotes,post_id,hero_ref_c)
            print("comment_insert_str: %s" % comment_insert_str)
            add_reddit_comment = (comment_insert_str)
            cursor.execute(add_reddit_comment)

            total_comments += 1
            db_log.write("%s ### %i Comments checked. Written to RedditComment table.\n" % (datetime.datetime.now(),total_comments))
            #connection.commit()

    # Commit all cursor changes
    connection.commit()

    db_log.write("%s ### DB commit all queries.\n" % (datetime.datetime.now()))

    # Close connection cursor
    cursor.close()

    db_log.write("%s ### DB cursor closed. \n" % (datetime.datetime.now()))

    # Close db log file
    db_log.close()

# Pull Hero data from Overwatch website
# Write data to local mysql database table - Hero
def pull_data_heroes(connection):
    # Grab connection cursor
    cursor = connection.cursor()

    resp = requests.get("https://playoverwatch.com/en-us/heroes/")
    resp_text = resp.text
    soup = BeautifulSoup(resp_text, 'html.parser')

    # Scrape hero names
    hero_names = []
    a_tag = soup.find_all('a')
    for tag in a_tag:
        hero = tag.get("data-hero-id")
        if hero:
            hero_names.append(hero)

    # Scrape hero roles
    role_names = []
    div_tag = soup.find_all('div')
    for tag in div_tag:
        role = tag.get("data-groups")
        if role:
            role = role.split("[\"")[1]
            role = role.split("\"]")[0]
            role = role.lower()
            role_names.append(role)

    # Test to see if all hero names and roles got scraped properly
    # for index in range(len(role_names)):
        # print(hero_names[index],role_names[index])
        # raw_input()

    # Insert hero names and roles into db
    for hero_index in range(len(role_names)):
        name = hero_names[hero_index]
        role = role_names[hero_index]
        add_hero = ("INSERT INTO Hero (name, role) VALUES ('%s', '%s')" % (name,role))
        # Insert new Hero
        cursor.execute(add_hero)
        hero_no = cursor.lastrowid

        # Database commit
        connection.commit()

    # Close connection cursor
    cursor.close()

# Load in positive and negative words from idiap.ch research institute.
def pull_pos_neg_words(connection):
    # Grab connection cursor
    cursor = connection.cursor()

    neg_f = open("../flat_files/negative-words.txt","r")
    neg_f_read = neg_f.readlines()
    for line in neg_f_read:
        word = line.strip()
        add_word = ("INSERT INTO SentimentWord(word, sentiment) VALUES ('%s', '%s')" % (word,'negative'))
        cursor.execute(add_word)
    neg_f.close()

    pos_f = open("../flat_files/positive-words.txt","r")
    pos_f_read = pos_f.readlines()
    for line in pos_f_read:
        word = line.strip()
        add_word = ("INSERT INTO SentimentWord(word, sentiment) VALUES ('%s', '%s')" % (word,'positive'))
        cursor.execute(add_word)
    pos_f.close()

    connection.commit()

    cursor.close()

# Queries the Hero table and grabs all hero names
def get_hero_list(connection):
    cursor = connection.cursor()

    cursor.execute("SELECT id,name FROM Hero")

    hero_list = []
    for (id,name) in cursor:
        hero_list.append((id,name))

    return hero_list

connection = db_connect()

hero_list = get_hero_list(connection)
#pull_pos_neg_words(connection)
pull_data_reddit(connection, hero_list, comment_count=100)

# Close db connection
connection.close()



# @TODO
# Data visualization for most mentioned in comments
# Data visualizaton for most popular words per hero
# Data visualization for most frequent hero combos mentioned

# Metrics covered in analyze.py:
    # Sentiment by hero - Top 5 positive heroes, Top 5 negative heroes
    # Top 5 Most mentioned heroes
    # Top 5 most popular words per hero
    # 2 Most popular heroes mentioned alongside each hero

import mysql.connector

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


# Get really simple sentiment on each post, on each hero
# Count how many positive and negative words are used, if there are more positive words... the post is positive.
# Count positive, negative, and neutral words per hero. Calculate positive, negative, and neutral sentiments per hero.
# Out of only positive and negative words, calculate positive and negative sentiment per hero (just remove neutral).
def getSentimentByHero(connection):
    cursor = connection.cursor()

    # Get all positive and negative words
    cursor.execute("select * from SentimentWord where sentiment = \'positive\'")
    positive_words = []
    for (id,word,sentiment) in cursor:
        positive_words.append(word)

    cursor.execute("select * from SentimentWord where sentiment = \'negative\'")
    negative_words = []
    for (id,word,sentiment) in cursor:
        negative_words.append(word)

    # Go through posts, go through each word.
    # Check to see if each word is positive, negative, or neutral.
    cursor.execute("select p.post, h.name from RedditPost p join Hero h on p.hero_ref_id = h.id;")
    sentiment_counts= {}
    for (post,name) in cursor:
        words = post.split(" ")
        if name not in sentiment_counts:
            sentiment_counts[name] = {"positive":[],"negative":[],"neutral":[]}
        for word in words:
            if word == name:
                continue
            if word in positive_words:
                sentiment_counts[name]["positive"].append(word)
            elif word in negative_words:
                sentiment_counts[name]["negative"].append(word)
            else:
                sentiment_counts[name]["neutral"].append(word)

    # Go through comments, go through each word.
    # Check to see if each word is positive, negative, or neutral.
    cursor.execute("select c.comment, h.name from RedditComment c join Hero h on c.hero_ref_id = h.id;")
    for (comment,name) in cursor:
        words = comment.split(" ")
        if name not in sentiment_counts:
            sentiment_counts[name] = {"positive":[],"negative":[],"neutral":[]}
        for word in words:
            if word == name:
                continue
            if word in positive_words:
                sentiment_counts[name]["positive"].append(word)
            elif word in negative_words:
                sentiment_counts[name]["negative"].append(word)
            else:
                sentiment_counts[name]["neutral"].append(word)

    return sentiment_counts

# Get heroes with most positive, negative, or neutral sentiments
# @param sentiment_type: positive, negative, neutral, or net (positive-negative)
def getHeroForMostSentiment(sentiment,sentiment_type,limit=5,rev=False):
    import operator

    hero_sentiments = {}
    if sentiment_type == "net":
        for hero in sentiment:
            hero_sentiments[hero] = len(sentiment[hero]["positive"]) - len(sentiment[hero]["negative"])
    else:
        for hero in sentiment:
            hero_sentiments[hero] = len(sentiment[hero][sentiment_type])


    sorted_sentiments = sorted(hero_sentiments.items(), key=operator.itemgetter(1), reverse=rev)

    return sorted_sentiments[:limit]


# Get most mentioned heroes
# @param type: post,comment
def getMostMentionedHeroes(connection):
    cursor = connection.cursor()

    cursor.execute("select *, (posts/totalPosts) as postRatio from (select h.id, h.name, count(distinct p.id) posts, (select count(distinct p2.id) from RedditPost p2)+0.0 as totalPosts from RedditPost p join Hero h on p.hero_ref_id = h.id group by h.id, h.name) d order by postRatio desc")

    heroes_mentioned = []
    for (id,name,posts,totalPosts,postRatio) in cursor:
        heroes_mentioned.append(('post',id,name,posts,float(totalPosts),float(postRatio)))

    cursor.execute("select *, (comments/totalComments) as commentRatio from (select h.id, h.name, count(distinct c.id) comments, (select count(distinct c2.id) from RedditComment c2)+0.0 as totalComments from RedditComment c join Hero h on c.hero_ref_id = h.id group by h.id, h.name) d order by commentRatio desc")
    for (id,name,comments,totalPosts,commentRatio) in cursor:
            heroes_mentioned.append(('comment',id,name,comments,float(totalPosts),float(commentRatio)))

    return heroes_mentioned

def getMostPopularWordsByHero(connection,limit=5):
    cursor = connection.cursor()

    # Get stop words
    stop_words_f = open("../flat_files/stop-words.txt","r")
    stop_words = []
    lines = stop_words_f.readlines()
    for line in lines:
        stop_word = line.strip()
        stop_words.append(stop_word)

    # Go through posts, go through each word.
    # Do a word count.
    cursor.execute("select p.post, h.name from RedditPost p join Hero h on p.hero_ref_id = h.id;")
    word_counts = {}
    for (post,name) in cursor:
        words = post.split(" ")
        if name not in word_counts:
            word_counts[name] = {}
        for word in words:
            if name in word or word in stop_words or word == '':
                continue
            if word not in word_counts[name]:
                word_counts[name][word] = 1
            else:
                word_counts[name][word] += 1

    cursor.reset()

    # Go through comment, go through each word.
    # Do a word count.
    import operator
    cursor.execute("select c.comment, h.name from RedditComment c join Hero h on c.hero_ref_id = h.id;")
    for (comment,name) in cursor:
        words = comment.split(" ")
        if name not in word_counts:
            word_counts[name] = {}
        for word in words:
            if name in word or word in stop_words or word == '':
                continue
            if word not in word_counts[name]:
                word_counts[name][word] = 1
            else:
                word_counts[name][word] += 1

    # Get most frequent words
    top_word_counts = {}
    for hero in word_counts:
        top_word_counts[hero] = sorted(word_counts[hero].items(), key=operator.itemgetter(1), reverse=True)[:limit]

    return top_word_counts

import itertools
def getMostMentionedHeroesByHero(connection,limit=2,top_limit=5):
    cursor = connection.cursor()

    # Get list of heroes
    heroes = []
    cursor.execute("select name from Hero")
    for (name) in cursor:
        heroes.append(name[0])

    # Go through posts, go through each word.
    # Count all the times another hero was mentioned.
    cursor.execute("select p.post from RedditPost p;")
    hero_together_counts = {}
    for (post) in cursor:
        post = post[0]
        heroes_mentioned = []
        words = post.split(" ")
        for word in words:
            if word in heroes:
                if word in heroes_mentioned: # If already found that hero...
                    continue
                heroes_mentioned.append(word)
        if len(heroes_mentioned) < 2:
            continue

        # Get combinations of all heroes mentioned in the current post
        heroes_mentioned_combos = itertools.combinations(heroes_mentioned,limit)

        # Go through each hero mentioned combo, sort the combo by hero name, and do a combo count.
        for combo in heroes_mentioned_combos:
            sorted_combo = sorted(combo)
            sorted_combo_str = ','.join(sorted_combo)
            if sorted_combo_str not in hero_together_counts:
                    hero_together_counts[sorted_combo_str] = 1
            else:
                hero_together_counts[sorted_combo_str] += 1

    # Go through comments, go through each word.
    # Count all the times another hero was mentioned.
    cursor.execute("select c.comment from RedditComment c;")
    for (comment) in cursor:
        comment = comment[0]
        heroes_mentioned = []
        words = comment.split(" ")
        for word in words:
            if word in heroes:
                if word in heroes_mentioned: # If already found that hero...
                    continue
                heroes_mentioned.append(word)
        if len(heroes_mentioned) < 2:
            continue

        # Get combinations of all heroes mentioned in the current post
        heroes_mentioned_combos = itertools.combinations(heroes_mentioned,limit)

        # Go through each hero mentioned combo, sort the combo by hero name, and do a combo count.
        for combo in heroes_mentioned_combos:
            sorted_combo = sorted(combo)
            sorted_combo_str = ','.join(sorted_combo)
            if sorted_combo_str not in hero_together_counts:
                    hero_together_counts[sorted_combo_str] = 1
            else:
                hero_together_counts[sorted_combo_str] += 1


    # Get top combo of heroes
    import operator
    top_hero_combos = sorted(hero_together_counts.items(), key=operator.itemgetter(1), reverse=True)[:top_limit]

    return top_hero_combos



# Returns data of hero
def getHero(connection,id=1,name=None):
    query = "select * from hero"

    where = False
    if id:
        query = query + (" where id = %i" % id)
        where = True
    if name:
        if where:
            query = query + (" and name = \'%s\'" % name)
        else:
            query = query + (" where name = \'%s\'" % name)

    print(query)
    cursor = connection.cursor()
    cursor.execute(query)

    results = []
    for row in cursor:
        results.append(row)

    return results


connection = db_connect()

# Sentiment Analysis
#sentiment = getSentimentByHero(connection)
#net_sentiment = getHeroForMostSentiment(sentiment,"net",limit=21,rev=True)
#print("Net Sentiment")
#names = []
#sent_val = []
#for pair in net_sentiment:
#    names.append(pair[0])
#    sent_val.append(pair[1])
#print(names)
#print(sent_val)

# Most Mentioned Heroes Analysis
most_mentioned = getMostMentionedHeroes(connection)
print("Most Mentioned Heroes - Posts")
names = []
posts = []
for record in most_mentioned:
    if record[0] != 'post':
        continue
    if str(record[2]) not in names:
        names.append(str(record[2]))
    posts.append(str(record[3]))
print(names)
print(posts)

# Most Frequently Mentioned Words
'''
word_counts = getMostPopularWordsByHero(connection)
print("Most Popular Word Counts\n {0}\n".format(word_counts))

# Get Most Frequent Combos of Heroes
most_mentioned_combos = getMostMentionedHeroesByHero(connection,limit=2,top_limit=5)
print("Most Mentioned Combos\n {0}\n".format(most_mentioned_combos))
'''
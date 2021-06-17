from os import mkdir
from os.path import exists, getsize, join
from random import randint
from json import dump
from datetime import datetime, timedelta

posts = []
COUNT = 1000

TARGET_DIR = 'test-data'
TARGET_FILE = 'posts.json'

if not exists(TARGET_DIR):
    mkdir(TARGET_DIR)

for i in range(COUNT):
    upvotes = randint(0, 100000)
    downvotes = randint(0, 100000)
    posts.append({
        'title': f'post_title_{i}',
        'text': f'post_text_{i}',
        'score': upvotes - downvotes,
        'votes': upvotes + downvotes,
        'user_id': '$user_id',
        'created_on': (datetime.now() - timedelta(seconds=randint(0, 24*3600*366))).timestamp()
    })

with open(join(TARGET_DIR, TARGET_FILE), 'w') as f:
    dump(posts, f)

print(f'Wrote {int(getsize(join(TARGET_DIR, TARGET_FILE))/1024)} KB to {join(TARGET_DIR, TARGET_FILE)}')

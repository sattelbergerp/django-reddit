from os import mkdir
from os.path import exists, getsize, join
from random import randint
from json import dump
from datetime import datetime, timedelta

total_comments = 0
def generate_comment(depth=0):
    global total_comments
    children = []
    if randint(0,3) == 0 and depth < 10:
        for i in range(randint(0,10)):
            children.append(generate_comment(depth=depth+1))
    total_comments += 1
    upvotes = randint(0, 100000)
    downvotes = randint(0, 100000)
    return {
                'target_class': 'reddit.models.Comment',
                'text': f'post_comment_{total_comments - 1}',
                'score': upvotes - downvotes,
                'votes': upvotes + downvotes,
                'user_id': '$user_id',
                'post': '$root',
                'parent': '$parent' if depth > 1 else None,
                'children': children,
                'created_on': (datetime.now() - timedelta(seconds=randint(0, 24*3600*366))).timestamp(),
            }

posts = []
COUNT = 10

TARGET_DIR = 'test-data'
TARGET_FILE = 'posts.json'

if not exists(TARGET_DIR):
    mkdir(TARGET_DIR)

for i in range(COUNT):
    upvotes = randint(0, 100000)
    downvotes = randint(0, 100000)
    posts.append({
        'target_class': 'reddit.models.Post',
        'title': f'post_title_{i}',
        'text': f'post_text_{i}',
        'score': upvotes - downvotes,
        'votes': upvotes + downvotes,
        'user_id': '$user_id',
        'comments': [generate_comment()],
        'created_on': (datetime.now() - timedelta(seconds=randint(0, 24*3600*366))).timestamp()
    })

with open(join(TARGET_DIR, TARGET_FILE), 'w') as f:
    dump(posts, f)

print(f'Wrote {int(getsize(join(TARGET_DIR, TARGET_FILE))/1024)} KB to {join(TARGET_DIR, TARGET_FILE)}')

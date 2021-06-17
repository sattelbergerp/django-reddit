from django.test import TestCase
from django.utils import timezone
from .models import Post, User, VotableManager
from json import load
from os.path import join
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

# Create your tests here.
def load_objects_from_file(type, file, context={}):
    with open(join('test-data', file)) as f:
        entries = load(f)
    return [create_object_from_data(type, data, context=context) for data in entries]

def create_object_from_data(type, data, context={}):
    obj = type()
    for key, value in data.items():
        if isinstance(value, str) and value.startswith('$'):
            setattr(obj, key, context[value[1:]])
        elif key!='created_on' or key!='updated_on':
            setattr(obj, key, value)
    obj.save()
    for key, value in data.items():
        if key=='created_on' or key=='updated_on':
            setattr(obj, key, make_aware(datetime.fromtimestamp(value)))
    obj.save()
    return obj

class PostVotableModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test1', password='pjkwvb86hj')
        self.user2 = User.objects.create(username='test2', password='pjkwvb86hj')
        self.user3 = User.objects.create(username='test3', password='pjkwvb86hj')
        self.posts = load_objects_from_file(Post, 'posts.json', context={'user_id': self.user.id})

    def test_sorting_by_hot_correctly_sorts_posts(self):
        db_sorted = Post.objects.sort()
        def sort_function(p):
            time_mod = int((timezone.now() - p.created_on).total_seconds()/3600/8)+1
            if p.score >= 0:
                return int(p.score / time_mod)
            else:
                return int(p.score * time_mod)
        py_sorted = sorted(self.posts, key=sort_function, reverse=True)
        self.assertQuerysetEqual(db_sorted, py_sorted)

    def test_sorting_by_newest_sorts_by_newest(self):
        db_sorted = Post.objects.sort(type=VotableManager.NEWEST)
        py_sorted = sorted(self.posts, key=lambda p: p.created_on, reverse=True)
        self.assertQuerysetEqual(db_sorted, py_sorted)

    def test_sorting_by_oldest_sorts_by_oldest(self):
        db_sorted = Post.objects.sort(type=VotableManager.OLDEST)
        py_sorted = sorted(self.posts, key=lambda p: p.created_on)
        self.assertQuerysetEqual(db_sorted, py_sorted)

    def test_sorting_by_top_all_time_correctly_sorts_posts(self):
        db_sorted = Post.objects.sort(type=VotableManager.TOP_ALL_TIME)
        py_sorted = sorted(self.posts, key=lambda p: p.score, reverse=True)
        self.assertQuerysetEqual(db_sorted, py_sorted)

    def test_sorting_by_top_past_year_correctly_sorts_and_filters_posts(self):
        db_sorted = Post.objects.sort(type=VotableManager.TOP_PAST_YEAR)
        py_sorted = sorted(self.posts, key=lambda p: p.score, reverse=True)
        py_sorted = filter(lambda p: p.created_on >= timezone.now() - timedelta(days=365), py_sorted)
        self.assertQuerysetEqual(db_sorted, py_sorted)

    def test_sorting_by_top_past_month_correctly_sorts_and_filters_posts(self):
        db_sorted = Post.objects.sort(type=VotableManager.TOP_PAST_MONTH)
        py_sorted = sorted(self.posts, key=lambda p: p.score, reverse=True)
        py_sorted = filter(lambda p: p.created_on >= timezone.now() - timedelta(days=31), py_sorted)
        self.assertQuerysetEqual(db_sorted, py_sorted)

    def test_sorting_by_top_past_week_correctly_sorts_and_filters_posts(self):
        db_sorted = Post.objects.sort(type=VotableManager.TOP_PAST_WEEK)
        py_sorted = sorted(self.posts, key=lambda p: p.score, reverse=True)
        py_sorted = filter(lambda p: p.created_on >= timezone.now() - timedelta(days=7), py_sorted)
        self.assertQuerysetEqual(db_sorted, py_sorted)
    
    def test_sorting_by_top_past_day_correctly_sorts_and_filters_posts(self):
        db_sorted = Post.objects.sort(type=VotableManager.TOP_PAST_DAY)
        py_sorted = sorted(self.posts, key=lambda p: p.score, reverse=True)
        py_sorted = filter(lambda p: p.created_on >= timezone.now() - timedelta(days=1), py_sorted)
        self.assertQuerysetEqual(db_sorted, py_sorted)

    
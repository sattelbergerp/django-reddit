from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import CASCADE
from django.db.models.expressions import Value
from django.db.models.fields import BigIntegerField, DecimalField
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from django.db.models import F, ExpressionWrapper
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.template.defaultfilters import slugify
from django.db.models import Case, Value, When

class Updateable(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class VotableManager(models.Manager):
    
    TOP_ALL_TIME = 'top-all-time'
    TOP_PAST_YEAR = 'top-past-year'
    TOP_PAST_MONTH = 'top-past-month'
    TOP_PAST_WEEK = 'top-past-week'
    TOP_PAST_DAY = 'top-past-day'
    NEWEST = 'newest'
    OLDEST = 'oldest'
    HOT = 'hot'

    def sort(self, type=None):
        if type == VotableManager.TOP_ALL_TIME:
            return self.order_by('-score')
        elif type == VotableManager.TOP_PAST_YEAR:
            
            return self.order_by('-score').filter(created_on__gte = timezone.now() - timedelta(days=365))
        elif type == VotableManager.TOP_PAST_MONTH:
            return self.order_by('-score').filter(created_on__gte = timezone.now() - timedelta(days=31))
        elif type == VotableManager.TOP_PAST_WEEK:
            return self.order_by('-score').filter(created_on__gte = timezone.now() - timedelta(days=7))
        elif type == VotableManager.TOP_PAST_DAY:
            return self.order_by('-score').filter(created_on__gte = timezone.now() - timedelta(days=1))
        elif type == VotableManager.NEWEST:
            return self.order_by('-created_on')
        elif type == VotableManager.OLDEST:
            return self.order_by('created_on')
        else:
            query = self.annotate(timesince = ExpressionWrapper(timezone.now() - F('created_on'), output_field=BigIntegerField()))
            query = query.annotate(timecompare=F('timesince') / 1000000 / 3600 / 8 + 1)
            return query.annotate(rating=Case(
                When(score__lt=0, then=F('score') * F('timecompare')), 
                default=F('score') / F('timecompare'),
                output_field=BigIntegerField())).order_by('-rating')


class Votable(Updateable):
    VOTE_TYPE_UPVOTE = 'u'
    VOTE_TYPE_DOWNVOTE = 'd'
    
    score = models.IntegerField(default=0)
    votes = models.IntegerField(default=0)
    user = models.ForeignKey('User', on_delete=CASCADE)

    objects = VotableManager()

    class Meta:
        abstract = True

    def get_votable_type_code(self):
        type_code = getattr(self, 'type_code', None)
        if not type_code or len(type_code) != 1:
            raise ValueError('Votable objects must define a single letter type code')

    """Returns 'u' for upvotes, 'd' for downvotes None if the user hasn't voted"""
    def get_vote(self, user):
        votable_type = self.get_votable_type_code()
        try:
            return Vote.get(user=user, target_type=votable_type, target=self.id).type
        except Vote.DoesNotExist:
            return None

    def vote(self, user, type):
        votable_type = self.get_votable_type_code()
        current_vote = self.get_vote(user)
        vote_change, score_change = 0, 0
        if type=='u':
            if current_vote == 'u':
                self.remove_vote(user, 'u')
                vote_change = -1
                score_change = -1
            else:
                downvoted = self.remove_vote(user, 'd')
                self.add_vote(user, 'u')
                vote_change += 0 if downvoted else 1
                score_change += 2 if downvoted else 1

        if type=='d':
            if current_vote == 'd':
                self.remove_vote(user, 'd')
                vote_change = -1
                score_change = 1
            else:
                upvoted = self.remove_vote(user, 'u')
                self.add_vote(user, 'd')
                vote_change += 0 if upvoted else 1
                score_change -= 2 if upvoted else 1
        
        if vote_change or score_change:
            self.votes += vote_change
            self.score += vote_change
            self.save()

    """Add a vote to the votes table does not affect cached scores or totals or check if a vote for this user already exists"""
    def add_vote(self, user, type):
        votable_type = self.get_votable_type_code()
        return Vote.objects.create(user=user, target_type=votable_type, target=self.id, type=type)

    def remove_vote(self, user, type):
        votable_type = self.get_votable_type_code()
        return Vote.objects.filter(user=user, target_type=votable_type, target=self.id, type=type).delete()[0]

class Vote(models.Model):

    VOTE_TYPE = (
        ('u', 'Upvote'),
        ('d', 'Downvote'),
    )
    type = models.CharField(max_length=1, choices=VOTE_TYPE, blank=True, null=True)
    target = models.BigIntegerField(default=0)
    target_type = models.CharField(max_length=1)
    user = models.ForeignKey('reddit.User', on_delete=models.CASCADE)

class User(AbstractUser):
    karma = models.IntegerField(default=0)
    pass

def validate_subreddit_name(value):
    if value in Subreddit.DISALLOWED_NAMES:
        raise ValidationError(_('Names can\'t be any of the following: %(disallowed_names)') % {'disallowed_names': ','.join(Subreddit.DISALLOWED_NAMES)})

class Subreddit(Updateable):
    DISALLOWED_NAMES = ['all', 'random']
    slug = models.SlugField(primary_key=True, max_length=100)
    name = models.TextField(max_length=100, validators=[validate_subreddit_name])
    
    owner = models.ForeignKey(to=User, on_delete=CASCADE)
    hidden = models.BooleanField(default=False)
    moderators = models.ManyToManyField(to=User, related_name='moderator')
    subscribers = models.ManyToManyField(to=User, related_name='subscriber')
    posts = models.ForeignKey(to='Post', on_delete=CASCADE)



class Post(Votable):
    type_code = 'p'

    title = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256)
    text = models.TextField(max_length=10000, null=True, blank=True)
    link = models.CharField(max_length=256, null=True, blank=True)

    objects = VotableManager()

    def is_text_post(self):
        return self.text != None

    def is_link_post(self):
        return self.link != None

    def clean(self, *args, **kwargs):
        if self.text and self.link:
            raise ValidationError(_('A post can contain a link or text content, not both'))
        if not self.text and not self.link:
            raise ValidationError(_('A post must contain either a link or text content'))
        super().clean(*args, **kwargs)

    @receiver(pre_save, sender='reddit.Post')
    def create_slug(sender, instance, **kwargs):
        instance.slug = slugify(instance.title[0:100])

    def __str__(self):
        return str(self.score)
    

class Comment(Votable):
    type_code = 'self'

    post = models.ForeignKey(Post, on_delete=CASCADE)
    parent = models.ForeignKey('self', on_delete=CASCADE, null=True, blank=True)
    text = models.TextField(max_length=10000)
    deleted = models.BooleanField(default=False)


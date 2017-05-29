from __future__ import absolute_import, unicode_literals
from django.db import models
from django.contrib.auth.models import User
import datetime


class Hashtags(models.Model):
    id = models.AutoField(primary_key=True)
    hashtag = models.CharField(max_length=200)


class Users(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    insta_login = models.CharField(max_length=200)
    insta_password = models.CharField(max_length=200)
    twitter_login = models.CharField(max_length=200, blank=True, null=True)
    twitter_password = models.CharField(max_length=200, blank=True, null=True)
    hashtags = models.ManyToManyField(Hashtags, through='Selected_hashtags')
    last_post_date= models.DateField(default=datetime.date.today)
    like_count= models.IntegerField(default=0)
    comment_count= models.IntegerField(default=0)
    follow_count = models.IntegerField(default=0)
    unfollow_count = models.IntegerField(default=0)
    followed_by = models.IntegerField(default=0)
    follows = models.IntegerField(default=0)
    insta_id= models.IntegerField(default=0)
    insta_followed_by = models.IntegerField(default=0)
    insta_follows = models.IntegerField(default=0)
    insta_media_count = models.IntegerField(default=0)
    insta_like_count = models.IntegerField(default=0)
    insta_comment_count = models.IntegerField(default=0)
    like_paused_to = models.IntegerField(default=0)
    insta_on = models.BooleanField(default=True)
    insta_likes_on= models.BooleanField(default=True)
    insta_comments_on= models.BooleanField(default=True)
    insta_follow_on= models.BooleanField(default=False)
    insta_unfollow_on= models.BooleanField(default=True)
    insta_who_follow_on = models.BooleanField(default=False)
    insta_who_followedby_on = models.BooleanField(default=False)
    insta_who_liked_on = models.BooleanField(default=False)

    insta_time_until=models.IntegerField(default=0)
    insta_trial_active=models.BooleanField(default=False)
    insta_paid_active = models.BooleanField(default=False)


class Influencers(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, default='')

class Selected_hashtags(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(Hashtags, on_delete=models.CASCADE)
    last_action_date = models.IntegerField(default=0)


class History(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    time_field = models.IntegerField()

    product = models.CharField(max_length=200, default='')
    action = models.CharField(max_length=200, default='')
    text = models.CharField(max_length=200, default='')

# class History2(models.Model):
#     user = models.ForeignKey(Users, on_delete=models.CASCADE)
#     time_field = models.IntegerField()
#
#     product = models.CharField(max_length=200, default='')
#     action = models.CharField(max_length=200, default='')
#     text = models.CharField(max_length=200, default='')


class AddCommentByCaption(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    caption_query=models.CharField(max_length=200, default='')
    comment_text=models.CharField(max_length=200, default='')

class Followed_Users(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    followed_id=models.IntegerField(default=0)
    followed_time= models.IntegerField(default=0)

class Locations(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    name=models.CharField(max_length=200, default='')
    num=models.IntegerField(default=0)
    slug=models.CharField(max_length=200, default='')
    last_action_date = models.IntegerField(default=0)

class HashtagForFollow(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    hashtag = models.CharField(max_length=200, default='')

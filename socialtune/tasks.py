from __future__ import absolute_import, unicode_literals
import django, os, datetime, random,sys

from django.conf import settings
sys.path.append('/home/niaz/work/socialtune')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "socialtune.settings")

django.setup()

import requests, json, re, time
from socialtune.models import Selected_hashtags, History, Users, AddCommentByCaption,Followed_Users, Locations
from celery import shared_task
import instagr

def unfollow(insta,user,follower_list,UNFOLLOW_LIMIT):
    if user.unfollow_count < UNFOLLOW_LIMIT and user.insta_unfollow_on and insta.last_unfollow_time <(time.time() - 35):
        followed_users = Followed_Users.objects.filter(user=user, followed_time__lt=(
            time.time() - 48 * 60 * 60)).all()
        for followed_user in followed_users:
            if int(followed_user.followed_id) not in follower_list:
                if insta.unfollow(followed_user.followed_id):

                    insta.last_unfollow_time = time.time()
                    user.unfollow_count += 1
                    user.save()
                    print('Unfollow', followed_user.followed_id)
                    followed_user.delete()

                    history = History(user=user, time_field=time.time(), product='I',
                                      action='UnFollow',
                                      text=str(followed_user.followed_id))

                    history.save()
                    break
                else:
                    print('Fail unfollow',followed_user.followed_id)

            else: pass

    return insta.last_unfollow_time

def follow(insta,user,n, FOLLOW_LIMIT):
    if user.follow_count < FOLLOW_LIMIT  and insta.last_follow_time < (time.time() - 50):
        if not Followed_Users.objects.filter(user=user,
                                             followed_id=n['owner']['id']).first():
            if insta.follow(n['owner']['id']):
                insta.last_follow_time = time.time()
                user.follow_count += 1
                user.save()
                follows = Followed_Users(user=user, followed_id=int(n['owner']['id']),
                                         followed_time=time.time())
                follows.save()
                history = History(user=user, time_field=time.time(), product='I',
                                  action='Follow',
                                  text=n['owner']['id'] + ' ' + n['code'] + ' ' )
                print('Follow', n['owner']['id'])
                history.save()

def comment(insta,user,n, tag, comment_list, COMMENT_LIMIT):
    if user.insta_comments_on:
        if n.get('caption', False):
            if n['date'] > tag.last_action_date and user.comment_count < COMMENT_LIMIT and insta.last_comment_time < (time.time() - 30):
                for c in comment_list:
                    if re.search(c.caption_query, n['caption'], re.S|re.I):
                        comments = c.comment_text.split('|')
                        comment = comments[random.randint(0, len(comments) - 1)]
                        if insta.add_comment(n['id'], comment):
                            insta.last_comment_time = time.time()
                            user.comment_count += 1
                            user.last_post_date = datetime.date.today()
                            history = History(user=user, time_field=time.time(),
                                              product='I',
                                              action='Comment',
                                              text=user.user.username + ' ' + n[
                                                  'code']  +' ' + comment)
                            history.save()
                            print(history.text)
                            return True
                        else:
                            print('comment Error')

        else:
            pass
    return False

def like(insta,user,n, tag, LIKE_LIMIT):
    if user.insta_likes_on:
        if int(n['date']) > int(tag.last_action_date) and user.like_count < LIKE_LIMIT:
            if user.like_paused_to:
                if user.like_paused_to<time.time():
                    user.like_paused_to=0
                    insta.like_paused_to=0
                    user.save()
                else:
                    return False
            time.sleep(5)
            if insta.like(n['id']):
                insta.last_like_time = time.time()
                user.like_count += 1
                user.last_post_date = datetime.date.today()
                history = History(user=user, time_field=time.time(), product='I', action='Like',
                                  text=user.user.username + ' ' + n['code'] )
                history.save()
                print(history.text)
                return True
            else:
                if insta.like_paused_to:
                    print('It looks like you were misusing this feature by going too fast. Freezing on 3 hours')
                    insta.like_paused_to=time.time()+(60*60*6)
                    user.like_paused_to=insta.like_paused_to
                    user.save()
                else:
                    print('Fail like in',n['code'] )
    return False


@shared_task
def task_1(user_id):
    LIKE_LIMIT = 800
    UNFOLLOW_LIMIT=300
    FOLLOW_LIMIT=200
    COMMENT_LIMIT=200

    user = Users.objects.filter(user_id=user_id).first()
    if user.last_post_date != datetime.date.today():
        user.like_count = 0
        user.comment_count = 0
        user.follow_count = 0
        user.unfollow_count = 0
        user.save()

    if user.like_count < LIKE_LIMIT :
        comment_list = AddCommentByCaption.objects.filter(user=user).all()
        hashtags = list(map(lambda x: (x.hashtag.hashtag, x.hashtag.id), list(Selected_hashtags.objects.filter(user_id=user.id).all())))
        locations = list(map(lambda x: (x.name, x.num,x.slug), Locations.objects.filter(user=user.id).all()))
        print(user_id, hashtags, locations)
        if hashtags or locations:
            insta = instagr.Insta(user.insta_login, user.insta_password)
            if insta.login():
                r=insta.like_count(user.insta_id)
                user.insta_like_count=r[0]
                user.insta_comment_count=r[1]
                user.insta_id = insta.user_id
                user.insta_followed_by=insta.user_followed_by
                user.insta_follows=insta.user_follows
                user.insta_media_count=insta.user_media_count
                user.save()

                follower_list=list(map(lambda x: int(x['id']),insta.get_followers(user.insta_id)))

                following_list = list(map(lambda x: int(x['id']), insta.get_followings(user.insta_id)))
                for following in Followed_Users.objects.filter(user=user).all():
                    if following.followed_id not in following_list:
                        Followed_Users.objects.filter(user=user, followed_id=following.followed_id).delete()
                        print('Deleted following',following.followed_id)


                # TODO {"status": "fail", "message": "This account can't be followed right now."}
                for location in locations:
                    r = insta.explore_location(location[1])
                    if r['location']['media']['nodes']:
                        print(r['location']['name'], r['location']['media']['count'])
                        tag = Locations.objects.filter(user_id=user.id, num=location[1]).first()

                        for n in r['location']['media']['nodes']:
                            insta.last_unfollow_time=unfollow(insta, user, follower_list,UNFOLLOW_LIMIT)
                            if like(insta, user, n, tag, LIKE_LIMIT):
                                    follow(insta, user, n, FOLLOW_LIMIT)
                                    comment(insta, user, n, tag, comment_list, COMMENT_LIMIT)
                        tag.last_action_date = r['location']['media']['nodes'][0]['date']
                        tag.save()

                for hashtag in hashtags:
                    r = insta.explore_tag(hashtag[0])
                    if r['tag']['media']['nodes']:
                        print(r['tag']['name'], r['tag']['media']['count'])
                        tag = Selected_hashtags.objects.filter(user_id=user.id, hashtag=hashtag[1]).first()

                        for n in r['tag']['media']['nodes']:
                            insta.last_unfollow_time=unfollow(insta, user, follower_list,UNFOLLOW_LIMIT)
                            if like(insta, user, n, tag, LIKE_LIMIT):

                                    follow(insta, user, n, FOLLOW_LIMIT)
                                    comment(insta,user,n, tag, comment_list,COMMENT_LIMIT)

                        tag.last_action_date = r['tag']['media']['nodes'][0]['date']
                        tag.save()
                user.save()

            else:
                print('Not logged as',user.user.username)
    else:
        print('No limit for', user.user.username)


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "socialtune.settings")
    django.setup()

    while True:
        start_t=time.time()
        for user in Users.objects.all():
            # if user.insta_login!='wonderfuldental' or user.insta_login!='juniakim89':
            #if user.insta_login =='wonderfuldental':
            if user.insta_on:
                task_1(user_id=user.user_id)
        t=int(time.time()-start_t)
        print('\nLoop ',t)
        time.sleep(60*30) # TODO адаптивная пауза

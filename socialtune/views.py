from __future__ import absolute_import, unicode_literals
import json, tweepy, random, datetime, time, re
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.conf import settings
from socialtune.models import  Selected_hashtags, Hashtags, Users, History, AddCommentByCaption, Locations, Influencers, HashtagForFollow
from .instagr import Insta
from .forms import UserCreateForm, InstaLoginChange
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import  csrf_exempt
import requests

def register(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        print(request.POST)
        print(str(form))
        if form.is_valid():
            form.save()
            return redirect('/')
        else:
            print('invalid')
    else:
        c = {}
        return render(request, 'socialtune/index.html', c)

    c = {}
    return render(request, 'socialtune/index.html', c)



def index(request):
    c={}
    return render(request, 'socialtune/index.html', c)

@login_required
def set(request):
    user = Users.objects.filter(user_id=request.user.id).first()
    if request.method == 'POST':
        if request.path=='/set':
            if not Selected_hashtags.objects.filter(user=Users.objects.filter(id=request.user.id).first(),hashtag=Hashtags.objects.filter(hashtag=request.POST['hashtag_name']).first()):
                hashtag=Hashtags.objects.filter(hashtag=request.POST['hashtag_name']).first()
                if not hashtag:
                    hashtag=Hashtags.objects.create(hashtag=request.POST['hashtag_name'])
                    hashtag.save()

                selected_hashtag=Selected_hashtags.objects.create(user=user, hashtag=hashtag)
                selected_hashtag.save()
                # return redirect('/set')
        elif request.path=='/del':
            print(request.POST)
            Selected_hashtags.objects.filter(user = user,hashtag=Hashtags.objects.filter(hashtag=request.POST['hashtag_name']).first()).delete()

        elif request.path=='/setc':

            add_comment=AddCommentByCaption.objects.create(user=user,comment_text=request.POST['comment_text'],caption_query=request.POST['caption_query'])
            add_comment.save()
        elif request.path == '/delc':
            print(request.POST)
            AddCommentByCaption.objects.filter(id=int(request.POST['id'])).all().delete()


            # return render(request, 'socialtune/set.html', c)
    comments=AddCommentByCaption.objects.filter(user=user).all()
    hashtags = list(map(lambda x: x.hashtag.hashtag, list(Selected_hashtags.objects.filter(user_id=user.id).all())))
    # print(hashtags)
    c = {'hashtags': hashtags,'comments':comments}
    return render(request, 'socialtune/set.html', c)

def login(request):
    return render(request, reverse("login"))

def f_t(s):

    if s=='true':
        return True
    else:
        return False


@login_required
def settings(request):
    menu_type=1
    user = Users.objects.filter(user_id=request.user.id).first()
    if request.method == 'POST':
        if request.POST['type'] == 'location_add':
            menu_type=3
            insta=Insta('','')
            location=insta.topsearch_place(request.POST['location_name'])
            #print(location)
            if location:
                location=location[0]
                l=Locations(user=user,name=location['place']['title'],slug=location['place']['slug'],num=location['place']['location']['pk'])
                l.save()
                #print(request.POST['location_name'],location['place']['title'],location['place']['slug'],location['place']['location']['pk'])
                del insta
        elif request.POST['type'] == 'toggles':
            user.insta_follow_on=f_t(request.POST['follow'])
            user.insta_unfollow_on=f_t(request.POST['unfollow'])
            user.insta_comments_on=f_t(request.POST['comments'])
            user.insta_on=f_t(request.POST['active'])
            user.insta_likes_on=f_t(request.POST['like'])
            user.insta_who_follow_on = f_t(request.POST['who_follow'])
            user.insta_who_followedby_on = f_t(request.POST['who_followedby'])
            user.insta_who_liked_on = f_t(request.POST['who_liked'])
            user.save()
            c={'result':'success'}
            return HttpResponse(json.dumps(c), content_type="application/json")

        elif request.POST['type'] == 'location_del':
            menu_type = 3
            Locations.objects.filter(user=user, name=request.POST['location_name']).all().delete()
            #print(request.POST['location_name'])
        elif request.POST['type'] == 'hashtag_add':
            if not Selected_hashtags.objects.filter(user=Users.objects.filter(user=request.user.id).first(),hashtag=Hashtags.objects.filter(hashtag=request.POST['hashtag_name'].lower()).first()):
                r=re.findall('(\w+)',request.POST['hashtag_name'].lower(), re.I)
                if r:
                    hashtag=Hashtags.objects.filter(hashtag=r[0]).first()
                    if not hashtag:
                        hashtag=Hashtags.objects.create(hashtag=r[0])
                        hashtag.save()

                    selected_hashtag=Selected_hashtags.objects.create(user=user, hashtag=hashtag)
                    selected_hashtag.save()
        elif request.POST['type'] == 'hashtag_del':
            Selected_hashtags.objects.filter(user=user, hashtag=Hashtags.objects.filter(
                hashtag=request.POST['hashtag_name']).first()).delete()

        elif request.POST['type'] == 'comment_add':
            menu_type=2
            add_comment = AddCommentByCaption.objects.create(user=user, comment_text=request.POST['comment_text'],
                                                             caption_query=request.POST['caption_query'])
            add_comment.save()
        elif request.POST['type'] == 'comment_del':
            menu_type=2
            AddCommentByCaption.objects.filter(id=int(request.POST['id'])).all().delete()
        elif request.POST['type'] == 'CA_del':
            menu_type = 4
            Influencers.objects.filter(user=user, name=request.POST['CA_name']).delete()

        elif request.POST['type'] == 'CA_add':
            menu_type = 4
            if not Influencers.objects.filter(user=user, name=request.POST['CA_name']):
                influencer = Influencers.objects.create(user=user, name=request.POST['CA_name'])
                influencer.save()

        elif request.POST['type'] == 'f_hashtag_add':
            menu_type = 4
            if not HashtagForFollow.objects.filter(user=user,hashtag=request.POST['f_hashtag_name'].lower()).first():
                r=re.findall('(\w+)',request.POST['f_hashtag_name'].lower(), re.I)
                if r:
                    f_hashtag=HashtagForFollow.objects.create(user=user,hashtag=request.POST['f_hashtag_name'].lower())
                    f_hashtag.save()

        elif request.POST['type'] == 'f_hashtag_del':
            menu_type = 4
            HashtagForFollow.objects.filter(user=user, hashtag=request.POST['f_hashtag_name']).delete()

    locations=list(map(lambda x: x.name,Locations.objects.filter(user=user.id).all()))
    comments = AddCommentByCaption.objects.filter(user=user).all()
    hashtags = list(map(lambda x: x.hashtag.hashtag, list(Selected_hashtags.objects.filter(user_id=user.id).all())))
    influencers=Influencers.objects.filter(user=user).all()
    f_hashtags = HashtagForFollow.objects.filter(user=user).all()

    c = {'f_hashtags':f_hashtags,'comments_count':user.insta_comment_count, 'likes_count':user.insta_like_count,'unfollow_count':user.unfollow_count, 'follow_count':user.follow_count, 'comment_count':user.comment_count, 'like_count':user.like_count,'follows_by':user.insta_followed_by,'follows':user.insta_follows,'media_count':user.insta_media_count, 'comments':comments, 'locations':locations, 'hashtags':hashtags,'menu_type':menu_type,'insta_follow_on':user.insta_follow_on,'insta_unfollow_on':user.insta_unfollow_on,'insta_comments_on':user.insta_comments_on,'insta_on':user.insta_on,'insta_likes_on':user.insta_likes_on,
         'insta_who_follow_on': user.insta_who_follow_on, 'insta_who_followedby_on': user.insta_who_followedby_on,
         'insta_who_liked_on': user.insta_who_liked_on,'influencers':influencers}
    return render(request, 'socialtune/settings.html', c)

@login_required
def profile(request):
    user = Users.objects.filter(user_id=request.user.id).first()
    insta = Insta(user.insta_login, user.insta_password)
    insta.login()

    if request.method == 'POST':
        form = InstaLoginChange(request.POST)
        # print(request.POST)
        # print(str(form))
        if form.is_valid():
            user.insta_login, user.insta_password=form.save()
            user.save()

    #         return redirect('profile')
    #     else:
    #         print('invalid')
    # else:
    #     c = {}
    #     return render(request, 'socialtune/index.html', c)
    #
    # c = {}
    # return render(request, 'socialtune/index.html', c)
    tm=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(user.insta_time_until))
    if user.insta_trial_active:
        message='Trial period active until '+tm
    elif user.insta_paid_active:
        message = 'Paid period active until '+tm
    else:
        message='No trial or paid period'

    c={}
    # c['notify_url']='http://niaztv.sytes.net:8000/ipn'+ str(request.user.id)
    c['notify_url'] = 'http://fatso.ml:8000/ipn' + str(request.user.id)
    c['message']=message
    c['insta_login']=user.insta_login
    c['insta_status']=insta.insta_status
    return render(request, 'socialtune/profile.html', c)


@login_required
def history(request):  # TODO надо переделать вывод
    user = Users.objects.filter(user_id=request.user.id).first()
    history = History.objects.filter(user=user).all()
    items=[]
    for h in history:
        item = {}
        item['time_field']=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(h.time_field))
        item['product']=h.product
        item['action']=h.action
        item['text']=h.text
        items.append(item)

        # print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(h.time_field)),h.product,h.action,h.text)
    c = {'item': items}
    return render(request, 'socialtune/history.html', c)

@login_required
def run(request):
    return

@csrf_exempt
def ipn(request,uid):
    VERIFY_URL_PROD = 'https://www.paypal.com/cgi-bin/webscr'
    VERIFY_URL_TEST = 'https://www.sandbox.paypal.com/cgi-bin/webscr'
    DAYS=30

    # Switch as appropriate
    VERIFY_URL = VERIFY_URL_TEST
    # user = Users.objects.filter(user_id=request.user.id).first()
    # print(request.user.id,user.user_id,user.id,uid)
    # print(request.POST)
    params={}
    # params=dict(request.POST)
    for p in request.POST.keys():
        params[p]=request.POST[p]
    params['cmd']= '_notify-validate'
    print(params)
    if True: #params['payment_status']=='Completed':
        headers = {'content-type': 'application/x-www-form-urlencoded', 'host': 'www.paypal.com'}
        r = requests.post(VERIFY_URL, params=params, headers=headers, verify=True)
        r.raise_for_status()

        # Check return message and take action as needed
        if r.text == 'VERIFIED':
            user = Users.objects.filter(user_id=uid).first()
            if params['txn_type']=='subscr_signup':
                user.insta_trial_active = True
                user.insta_time_until += DAYS * 10 * 60 * 60
            elif params['txn_type']=='subscr_payment':
                user.insta_trial_active = False
                user.insta_paid_active=True
                user.insta_time_until+= DAYS*24*60*60
            elif params['txn_type'] == 'subscr_cancel':
                user.insta_trial_active = False
                user.insta_paid_active = False

                user.insta_time_until = time.time()
            user.save()
            print('paid',uid, user.insta_login)
        elif r.text == 'INVALID':
            pass
        else:
            pass
    # {'payment_type': 'instant', 'mc_fee': '0.69', 'business': 'niaztv@yandex.ru', 'payment_fee': '0.69',
    #  'residence_country': 'RU', 'item_name': 'One month', 'txn_id': '7LM31750EK1739002',
    #  'receiver_email': 'niaztv@yandex.ru', 'test_ipn': '1', 'mc_gross': '10.00',
    #  'payer_email': 'niaztv-buyer@gmail.com', 'payer_id': '9WWVEM5AVAAZA',
    #  'verify_sign': 'ApZwcZsoP.0EhLY44k88Z0WcxxqnARkMmt40eowq2JRo1BagCOKKeDAX', 'payment_gross': '10.00',
    #  'charset': 'windows-1252', 'ipn_track_id': 'a87768643f718', 'receiver_id': 'BYB7XK6YWNLBE',
    #  'notify_version': '3.8', 'transaction_subject': '', 'custom': '', 'quantity': '1', 'first_name': 'test',
    #  'txn_type': 'web_accept', 'payer_status': 'verified', 'last_name': 'buyer', 'item_number': '',
    #  'payment_date': '10:49:13 Apr 02, 2017 PDT', 'mc_currency': 'USD', 'protection_eligibility': 'Ineligible',
    #  'payment_status': 'Completed', 'cmd': '_notify-validate'}

    c = {'result': 'success'}
    return HttpResponse(json.dumps(c), content_type="application/json")



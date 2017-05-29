import time, requests, json, re

class Insta():
    def __init__(self, username, password):
        self.insta_status = 'unknow'
        self.username = username
        self.password = password
        self.last_follow_time=0
        self.last_unfollow_time = 0
        self.last_comment_time = 0
        self.last_like_time=0
        self.likes_count=0
        self.comments_count=0
        self.already_liked=[]
        self.like_paused_to =0
        self.ses = requests.Session()
        self.ses.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
                            'Connection': 'keep-alive',
                            'Cache-Control': 'max-age=0',
                            'Accept-Encoding': 'gzip, deflate, sdch, br',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'origin': 'https://www.instagram.com',
                            'Referer': 'https://www.instagram.com',
                            'Host': 'www.instagram.com'
                            }

    def login(self):
        param = {'username': self.username, 'password': self.password}

        response = self.ses.get('https://www.instagram.com', timeout=10)

        self.csrftoken = response.cookies.get_dict()['csrftoken']
        self.ses.headers.update({'x-csrftoken': str(self.csrftoken)})

        response = self.ses.post('https://www.instagram.com/accounts/login/ajax/', data=param, timeout=10)
        if response.status_code == requests.codes.ok:
            #print(response.text)
            r=json.loads(response.text)
            if r['authenticated']!=True:
                self.insta_status = 'False authenticated'
                print('False authentcated')
                return False
            response = self.ses.get('https://www.instagram.com/', timeout=10)
            # print(response.text)
            print('Logged as', self.username)
            self.insta_status = 'ok'
            response = self.ses.get('https://www.instagram.com/'+self.username+'?__a=1', timeout=10)
            try:
                r = json.loads(response.text)
            except json.decoder.JSONDecodeError:
                # print(response.text)
                print(response.status_code)

            #print(r)
            self.user_id=r['user']['id']
            self.user_followed_by=r['user']['followed_by']['count']
            self.user_follows=r['user']['follows']['count']
            self.user_media_count= r['user']['media']['count']

            self.csrftoken = response.cookies.get_dict().get('csrftoken', self.csrftoken)
            self.ses.headers.update({'x-csrftoken': str(self.csrftoken)})
            # print(response.cookies.get_dict())
            return True
        elif response.status_code == 400:
            r = json.loads(response.text)
            if r['message']=='checkpoint_required':
                self.insta_status='checkpoint required'
                print("CHECKPOINT")
                print(r)
            return False
        else:
            print(response.status_code, response.text)
            print('Login Error')
            return False

    def get_query(self,url,params={}):
        url = 'https://www.instagram.com/' + url
        while True:
            try:
                response = self.ses.get( url, params=params, timeout=10)
            except requests.exceptions.RequestException as e:
                print(e)
                time.sleep(15)
                continue

            self.csrftoken = response.cookies.get_dict().get('csrftoken', self.csrftoken)
            self.ses.headers.update({'x-csrftoken': str(self.csrftoken)})
            try:
                r = json.loads(response.text)
            except json.decoder.JSONDecodeError:
                if re.search('Sorry, something went wrong', response.text):
                    print('Sorry, something went wrong')
                    time.sleep(15)
                    continue
                elif re.search('5xx Server Error', response.text):
                    print('5xx Server Error')
                    time.sleep(15)
                    continue
                else:
                    print('JD get error')
                    print(response.text)
                    print(response.status_code)
                break
            break


        # print(json.dumps(r, indent=4))
        return r


    def post_query(self,t,url,params={} ):
        self.ses.headers.update(
            {'Accept': '*/*',  'Content-Type': 'application/x-www-form-urlencoded'})
        self.ses.headers.update({'x-requested-with': 'XMLHttpRequest', 'x-instagram-ajax': '1'})

        error_count=0
        url='https://www.instagram.com/'+url
        while True:
            if error_count>=3:
                print('Too many error')
                return False

            try:
                if t=='post':
                    response = self.ses.post(url,data=params,  timeout=10)
                elif t=='get':
                    response = self.ses.get(url, params=params, timeout=10)
            except requests.exceptions.RequestException as e:
                print('POST QUERY',e)
                time.sleep(60)
                error_count += 1
                continue
            cs = response.cookies.get_dict().get('csrftoken', None)
            if cs:
                self.csrftoken = cs
                cs=response.cookies.get_dict().get('csrftoken', self.csrftoken)
                self.ses.headers.update({'x-csrftoken': str(self.csrftoken)})
            if response.status_code == 400:
                if re.search('been blocked from using', response.text):

                    self.like_paused_to=1
                    return False
                else:
                    print('Probably deleted', response.text)
                return False
            elif response.status_code == 404:
                print('404 error', response.status_code, url, params)
                return False
            elif response.status_code != requests.codes.ok:
                if re.search('Sorry, too many requests. Please try again later.', response.text):
                    print(response.status_code, 'Too many requests, wait 180 sec')
                    time.sleep(180)
                    error_count+=1
                    continue
                elif re.search('temporarily blocked', response.text):
                    print(response.status_code, response.text, 'temporarily blocked')
                    time.sleep(60 * 60)
                    return None

            try:
                r = json.loads(response.text)
            except:
                if re.search('Sorry, something went wrong', response.text):
                    print('Sorry, something went wrong')
                    time.sleep(15)
                    error_count += 1
                    continue
                elif re.search('5xx Server Error', response.text):
                    print('5xx Server Error')
                    time.sleep(15)
                    error_count += 1
                    continue
                else:
                    print('Json Decode error',response.status_code, url,params )
                    print(response.text)
                    print('sleep 15 sec')
                    time.sleep(15)
                    error_count += 1
                    continue
            if r.get('status',False):
                if r['status'] == 'fail':
                    print(r)
                    time.sleep(180)
                    continue


            break

        return r
        st = r['status']

    def get_user_id_from_username(self,username):
        r=self.post_query('get',str(username)+'/?__a=1')
        if r and r.get('user',False) and r['user'].get('id',False):
            return r['user']['id']
        return None

    def get_user_followers(self,username):
        user_id = self.get_user_id_from_username(username)
        if user_id:
            nodes=self.get_followers( user_id)
            return list(map(lambda x: x['username'],nodes))
        return None

    def get_user_followings(self, username):
        user_id = self.get_user_id_from_username(username)
        if user_id:
            nodes = self.get_followings(user_id)
            return list(map(lambda x: x['username'], nodes))
        return None

    def get_followers(self, user_id):
        params={}
        params['ref']='relationships::follow_list'
        p='first('
        nodes=[]
        while True:
            params['q']='ig_user('+str(user_id)+'){followed_by.'+p+'50){count,page_info{end_cursor,has_next_page},nodes{id,followed_by_viewer,requested_by_viewer,username}}}'
            r=self.post_query('post','query/',params)
            r = r['followed_by']
            # print(r)
            # print(len(r['nodes']))
            nodes+=r['nodes']
            if not r['page_info']['has_next_page']:
                break
            p='after('+r['page_info']['end_cursor']+','
        # print(len(nodes))
        return nodes

    def get_followings(self, user_id):
        params={}
        params['ref']='relationships::follow_list'
        p='first('
        nodes=[]
        while True:
            params['q']='ig_user('+str(user_id)+'){follows.'+p+'50){count,page_info{end_cursor,has_next_page},nodes{id,followed_by_viewer,requested_by_viewer,username}}}'
            r=self.post_query('post','query/',params)
            if not r.get('follows',False):
                print('Not follows',r)
                return []
            r = r['follows']
            # print(r)
            # print(len(r['nodes']))
            nodes+=r['nodes']
            if not r['page_info']['has_next_page']:
                break
            p='after('+r['page_info']['end_cursor']+','
        # print(len(nodes))
        return nodes

    def get_user_posts(self, username):
        user_id=self.get_user_id_from_username(username)
        if user_id:
            params = {}
            params['ref'] = 'users::show'
            p='first('
            nodes=[]
            while True:
                params['q']='ig_user('+str(user_id)+'){media.'+p+'50){count,page_info{end_cursor,has_next_page},nodes{id,date, code}}}'
                r=self.post_query('post','query/',params)

                if not r.get('media', False):
                    print('NO MEDIA',r)
                    return []
                nodes+= r['media']['nodes']
                break  # only first page
                if not r['media']['page_info']['has_next_page']:
                    break
                if not r['media']['page_info']['end_cursor']:
                    break
                try:
                    p='after('+r['media']['page_info']['end_cursor']+','
                except:
                    print(r)
                    exit()
            return list(map(lambda x: x['code'], nodes))
        return None

    def get_commenters_from_post(self,post_code):
        users_list=[]
        r = self.post_query('get', 'p/' +post_code+'/?__a=1')
        if r and r.get('media',False) and r['media'].get('comments',False) and r['media']['comments'].get('nodes',False):
            for n in r['media']['comments']['nodes']:
                users_list.append(n['user']['username'])
            return users_list
        return None

    def get_likers_from_post(self,post_code):
        users_list=[]
        r = self.post_query('get', 'p/' +post_code+'/?__a=1')
        if r and r.get('media',False) and r['media'].get('likes',False) and r['media']['likes'].get('nodes',False):
            for n in r['media']['likes']['nodes']:
                users_list.append(n['user']['username'])
            return users_list
        return None

    def like_count(self,user_id):
        params = {}
        params['ref'] = 'users::show'

        p='first('
        nodes=[]
        while True:
            params['q']='ig_user('+str(user_id)+'){media.'+p+'50){count,page_info{end_cursor,has_next_page},nodes{id,comments{count},likes{count}}}}'
            r=self.post_query('post','query/',params)
            if not r.get('media', False):
                print('NO MEDIA',r)
                return 0,0
            nodes+= r['media']['nodes']
            # print(r)
            # print(len(r['nodes']))

            if not r['media']['page_info']['has_next_page']:
                break
            p='after('+r['media']['page_info']['end_cursor']+','
        # print(len(nodes))
        likes=0
        comments=0
        for node in nodes:
            likes+=node['likes']['count']
            comments+=node['comments']['count']
        print('Media:',len(nodes),' Likes:', likes,' Comments:',comments)
        self.likes_count = likes
        self.comments_count = comments
        return likes,comments

    def like(self, post_id):
        if post_id in self.already_liked:
            print('Already liked')
            return False

        r = self.post_query('post','web/likes/' + str(post_id) + '/like/')
        if r:
            st = r['status']

            if st == 'ok':
                self.already_liked.append(post_id)
                return True
        #print('Like error',r)
        return False

    def dislike(self, post_id):
        self.ses.headers.update(
            {'Accept': '*/*', 'x-compress': 'null', 'Content-Type': 'application/x-www-form-urlencoded'})
        self.ses.headers.update({'x-requested-with': 'XMLHttpRequest', 'x-instagram-ajax': '1'})

        r = self.post_query('post','web/likes/' + str(post_id) + '/unlike/')
        st = r['status']
        if st == 'ok':
            return True

        return False

    def add_comment(self, post_id, text):
        self.ses.headers.update(
            {'Accept': '*/*', 'x-compress': 'null', 'Content-Type': 'application/x-www-form-urlencoded'})
        self.ses.headers.update({'x-requested-with': 'XMLHttpRequest', 'x-instagram-ajax': '1'})

        params = {'comment_text': str(text)}

        r = self.post_query('post','web/comments/' + str(post_id) + '/add/', params)
        if r:
            st=r['status']
            if st == 'ok':
                # self.ses.headers.update( { 'Content-Type': 'application/json'})
                # response = self.ses.post('https://www.instagram.com/ajax/bz', timeout=10)

                return True

        return False

    def explore_tag(self, hashtag):
        hashtag=hashtag.lower().strip(' ')
        param = {'__a': '1'}
        self.ses.headers.update({'accept': '*/*'})
        self.ses.headers.update({'x-requested-with': 'XMLHttpRequest'})

        r=self.post_query('get','explore/tags/' + hashtag + '/', param)
        return r

    def explore_location(self, place):
        param = {'__a': '1'}
        self.ses.headers.update({'accept': '*/*'})
        self.ses.headers.update({'x-requested-with': 'XMLHttpRequest'})
        r= self.post_query('get','explore/locations/' + str(place) + '/', param)
        return r

    def topsearch_place(self,name):
        r=self.post_query('get','web/search/topsearch/?context=place&query='+name)
        if r:
            return r['places']
        else:
            return None

    def follow(self,user_id):
        r= self.post_query('post','web/friendships/' + str(user_id) + '/follow/')
        if r:
            st = r['status']
            if st == 'ok':
                return True

        return False

    def unfollow(self, user_id):
        r=self.post_query('post','web/friendships/'+str(user_id)+'/unfollow/')
        if r:
            st = r['status']
            if st == 'ok':
                return True
            else:
                print('UNFOLLOW STATUS NOT OK', r, user_id)
        return False

    # def __repr__(self):
    #     return self.username

# Probably deleted {"message": "This account can't be followed right now.", "status": "fail"}

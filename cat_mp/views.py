# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.context_processors import csrf
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import utils
import logging
import time
from .forms import *
from .models import *
from crypt import encrypt, decrypt

# Create your views here.
logger = logging.getLogger('cat_mp_info')
mark = logging.getLogger('cat_mp_mark')

@csrf_exempt
def index(request):
    context = {}
    context.update(csrf(request))
    return render_to_response('index.html', context)

@csrf_exempt
def login(request):
    data = {'ret_code':0, 'ret_data':{}}
    try:
        if request.method == 'POST':
            req_data = json.loads(request.body)
        else:
            req_data = request.GET

        jscode = req_data['jscode']
        sess = utils.http_get(config.JSCODE_SESSION_URL + jscode)
        if 'openid' in sess:
            sess_key = utils.save_session(sess)
            if sess_key:
                data['ret_code'] = 1
                data['sess_key'] = sess_key
            else:
                data['msg'] = 'save session error.'
            mark.info('%s\t%s\t%s\tlogin' % (sess['openid'], utils.getuip(request), time.strftime("%Y-%m-%d %H:%M:%S")))
        else:
            data['msg'] = 'fetch session error'
            logger.error(str(sess))

    except Exception as err:
        data['msg'] = 'program or internet error.'
        logger.error(str(err))

    res = json.dumps(data, ensure_ascii=False)
    return HttpResponse(res, content_type="application/json")

@csrf_exempt
def save_uinfo(request):
    data = {'ret_code':0, 'ret_data':{}}
    try:
        if request.method == 'POST':
            req_data = json.loads(request.body)
        else:
            req_data = request.GET

        sess_key = req_data['sess_key']
        sess = utils.get_session(sess_key)
        sc = User.objects.filter(openid=sess['openid'])
        if sc.count() <= 0:
            User.objects.create(openid=sess['openid'], avatarUrl=req_data['avatarUrl'], nickName=req_data['nickName'], gender=req_data['gender'])
        else:
            user = sc.first()
            user.avatarUrl = req_data['avatarUrl']
            user.nickName = req_data['nickName']
            user.gender = req_data['gender']
            user.save()

        data['ret_code'] = 1
        mark.info('%s\t%s\t%s\tsave_uinfo' % (sess['openid'], utils.getuip(request), time.strftime("%Y-%m-%d %H:%M:%S")))

    except Exception as err:
        data['msg'] = 'program or internet error.'
        logger.error(str(err))

    res = json.dumps(data, ensure_ascii=False)
    return HttpResponse(res, content_type="application/json")

@csrf_exempt
def upload_test(request):
    return render_to_response('upload.html')

@csrf_exempt
def upload(request):
    data = {'ret_code':0, 'ret_data':{}}
    try:
        if request.method == 'POST':
            #for f in request.FILES.getlist('file'):
            form = ImageForm(request.POST, request.FILES)

            if form.is_valid():
                #print form.cleaned_data
                sess_key = form.cleaned_data['sess_key']
                sess = utils.get_session(sess_key)
                image = Image()
                image.title = form.cleaned_data['title']
                image.content= form.cleaned_data['content']
                image.fpath = form.cleaned_data['fpath']
                image.album_id= form.cleaned_data['album_id']
                image.index = int(form.cleaned_data['index'])
                image.openid = sess['openid']
                image.save()

                data['ret_code'] = 1
            else:
                data['msg'] = str(form.errors)

    except Exception as err:
        data['msg'] = 'program error.'
        logger.error(str(err))

    res = json.dumps(data, ensure_ascii=False)
    return HttpResponse(res, content_type="application/json")

@csrf_exempt
def get_album_list(request):
    data = {'ret_code':0, 'ret_data':{'image_list':[]}}
    try:
        if request.method == 'POST':
            req_data = json.loads(request.body)
        else:
            req_data = request.GET

        page_index = int(req_data.get('page_index', 0))
        page_count = int(req_data.get('page_count', 10))

        sess = utils.get_session(req_data['sess_key'])
        objs = Image.objects.filter(openid=sess['openid']).values("album_id").order_by("-album_id").distinct()
        for obj in objs[page_index : page_index+page_count]:
            m_images = Image.objects.filter(openid=sess['openid'], album_id=obj['album_id'], index=0)
            if m_images.count() > 0:
                data['ret_data']['image_list'].append(m_images[0].todict())
        data['ret_code'] = 1

    except Exception as err:
        data['msg'] = 'program or internet error.'
        logger.error(str(err))
    res = json.dumps(data, ensure_ascii=False)
    return HttpResponse(res, content_type="application/json")

@csrf_exempt
def get_album_info(request):
    data = {'ret_code':0, 'ret_data':{'image_list':[]}}
    try:
        if request.method == 'POST':
            req_data = json.loads(request.body)
        else:
            req_data = request.GET

        sess = utils.get_session(req_data['sess_key'])
        m_images = Image.objects.filter(openid=sess['openid'], album_id=req_data['album_id'])
        for m_image in m_images:
            data['ret_data']['image_list'].append(m_image.todict())
        data['ret_code'] = 1

    except Exception as err:
        data['msg'] = 'program or internet error.'
        logger.error(str(err))
    res = json.dumps(data, ensure_ascii=False)
    return HttpResponse(res, content_type="application/json")

@csrf_exempt
def prepay(request):
    data = {'ret_code':0, 'ret_data':{}}
    try:
        if request.method == 'POST':
            params = utils.get_prepay_params(request)
            ret = utils.http_post(config.UnifiedOrder_URL, params, trans2xml=True)
            if 'return_code' in ret and ret['return_code'] == 'SUCCESS' and 'result_code' in ret and ret['result_code'] == 'SUCCESS':
                data['ret_code'] = 1
                data['ret_data']['prepay_id'] = ret['prepay_id']

    except Exception as err:
        logger.error(str(err))

    res = json.dumps(data, ensure_ascii=False)
    return HttpResponse(res, content_type="application/json")

@csrf_exempt
def pay_notify(request):
    data = {'ret_code':0, 'ret_data':{}}
    print 'pay_notify.'
    res = json.dumps(data, ensure_ascii=False)
    return HttpResponse(res, content_type="application/json")

@csrf_exempt
def reward_test(request):
    return render_to_response('reward.html')

@csrf_exempt
def reward(request):
    data = {'ret_code':0, 'ret_data':{}}
    try:
        if request.method == 'POST':
            req_data = json.loads(request.body)
        else:
            req_data = request.GET

        reward = Reward()
        sess = utils.get_session(req_data['sess_key'])
        reward.ropenid = sess['openid']
        reward.amount = float(req_data['amount'])
        reward.album_id = req_data['album_id'] 
        reward.rtime = time.strftime('%Y-%m-%d %H:%M:%S')
        #reward.openid = encrypt(req_data['rid']) 
        sc = Image.objects.filter(album_id=reward.album_id)
        if sc.count() <= 0:
            data['msg'] = 'album not exist!'
        else:
            reward.openid = sc[0].openid
            reward.save()
            data['ret_code'] = 1

    except Exception as err:
        data['msg'] = 'program or internet error.'
        logger.error(str(err))

    res = json.dumps(data, ensure_ascii=False)
    return HttpResponse(res, content_type="application/json")

def get_rewards(request):
    data = {'ret_code':0, 'ret_data':{'rewards':[]}}
    try:
        if request.method == 'POST':
            req_data = json.loads(request.body)
        else:
            req_data = request.GET

        reward = Reward()
        sess = utils.get_session(req_data['sess_key'])
        page_index = int(req_data.get('page_index', 0))
        page_count = int(req_data.get('page_count', 10))
        reward.openid = sess['openid']
        if 'album_id' in req_data:
            m_rewards = Reward.objects.filter(openid=sess['openid'], album_id=req_data['album_id']).order_by("-rtime")[page_index : page_index+page_count]
        else:
            m_rewards = Reward.objects.filter(openid=sess['openid']).order_by("-rtime")[page_index : page_index+page_count]

        for m_reward in m_rewards:
            data['ret_data']['rewards'].append(m_reward.todict())

        data['ret_code'] = 1

    except Exception as err:
        data['msg'] = 'program or internet error.'
        logger.error(str(err))

    res = json.dumps(data, ensure_ascii=False)
    return HttpResponse(res, content_type="application/json")

def get_wxcode(request):
    data = {'ret_code':0, 'ret_data':{}}
    #try:
    if request.method == 'POST':
        req_data = json.loads(request.body)
    else:
        req_data = request.GET

    access_token = utils.get_and_update_access_token()
    if access_token is not None:
        scene = req_data.get('scene', '-1')
        if 'path' in req_data:
            _data = {'scene': scene, 'path': req_data['path']}
        else:
            _data = {'scene': scene}

        print _data

        wxcode_content = utils.http_post(config.WXACODE_URL + access_token, _data, decode_data=False)
        if len(wxcode_content) < 1024:
            data['msg'] = 'data format error.'
        else:
            filename = str(uuid.uuid1()) + ".jpeg"
            save_path = '/'.join([config.IMAGE_ROOT, filename])
            with open(save_path, 'wb') as f_wxcode:
                f_wxcode.write(wxcode_content)
                data['ret_code'] = 1
                data['ret_data']['wxcode'] = config.DATA_URL + filename 
    else:
        data['msg'] = 'fetch access_token or data error.'

    #except Exception as err:
    #    data['msg'] = 'program or internet error.'
    #    logger.error(str(err))

    res = json.dumps(data, ensure_ascii=False)
    return HttpResponse(res, content_type="application/json")
            
            

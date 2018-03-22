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
    data = {'ret_code':0}
    try:
        if request.method == 'POST':
            POST = json.loads(request.body)
            jscode = POST['jscode']
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
def upload(request):
    data = {'ret_code':0}
    try:
        if request.method == 'POST':
            #for f in request.FILES.getlist('file'):
            form = ImageForm(request.POST, request.FILES)
            if form.is_valid():
                sess_key = form.cleaned_data['sess_key']
                sess = utils.get_session(sess_key)
                image = Image()
                image.title = form.cleaned_data['title']
                image.fpath = form.cleaned_data['fpath']
                image.ftime = form.cleaned_data['ftime']
                #image.ftime = time.strftime('%Y-%m-%d %H:%M:%S')
                image.openid = sess['openid']
                image.save()

                data['ret_code'] = 1
            else:
                data['msg'] = str(form.errors)
        else:
            return render_to_response('upload.html')

    except Exception as err:
        data['msg'] = 'program error.'
        logger.error(str(err))

    res = json.dumps(data, ensure_ascii=False)
    return HttpResponse(res, content_type="application/json")

@csrf_exempt
def download(request):
    data = {'ret_code':0, 'images':[]}
    try:
        if request.method == 'GET':
            sess_key = request.GET['sess_key']
        else:
            sess_key = request.POST['sess_key']
        sess = utils.get_session(sess_key)
        images = Image.objects.filter(openid=sess['openid'])
        for image in images:
            data['images'].append(image.todict())

        data['ret_code'] = 1

    except Exception as err:
        data['msg'] = 'program or internet error.'
        logger.error(str(err))
    res = json.dumps(data, ensure_ascii=False)
    return HttpResponse(res, content_type="application/json")

@csrf_exempt
def prepay(request):
    data = {'ret_code':0}
    try:
        if request.method == 'POST':
            params = utils.get_prepay_params(request)
            ret = utils.http_post(config.UnifiedOrder_URL, params)
            if 'return_code' in ret and ret['return_code'] == 'SUCCESS' and 'result_code' in ret and ret['result_code'] == 'SUCCESS':
                data['ret_code'] = 1
                data['prepay_id'] = ret['prepay_id']

    except Exception as err:
        logger.error(str(err))

    res = json.dumps(data, ensure_ascii=False)
    return HttpResponse(res, content_type="application/json")

@csrf_exempt
def pay_notify(request):
    data = {'ret_code':0}
    print 'pay_notify.'
    res = json.dumps(data, ensure_ascii=False)
    return HttpResponse(res, content_type="application/json")

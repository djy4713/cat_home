# -*- coding: utf-8 -*-
import urllib
import urllib2
import json
import config
import uuid
import hashlib
import datetime
import xml.etree.ElementTree as ET
from rediscluster import StrictRedisCluster
import time

rc = StrictRedisCluster(startup_nodes=config.startup_nodes, decode_responses=True)

def save_session(sess):
    key = str(uuid.uuid1())
    value = json.dumps(sess)
    ret = rc.setex(key, config.EX_SESSION_TIME, value)
    if ret:
        return key
    else:
        return None

def get_session(key):
    value = rc.get(key)
    sess = json.loads(value)
    return sess

def get_and_update_access_token():
    access_token = None
    if rc.exists(config.ACCESS_TOKEN):
        access_token = rc.get(config.ACCESS_TOKEN) 
    else:
        _data = http_get(config.ACCESS_TOKEN_URL)
        if config.ACCESS_TOKEN in _data:
            access_token = _data[config.ACCESS_TOKEN]
            expires_in = _data['expires_in']
            rc.setex(config.ACCESS_TOKEN, expires_in - 300, access_token)
    return access_token

def exists_key(key):
    return rc.exists(key)

def get_openid(sess_key):
    sess = get_session(sess_key)
    return sess['openid'].encode('utf-8')

def getuip(request):
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip =  request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    return ip

def dict_to_param(data):
    up = None
    items = data.items()
    items.sort()
    for key, value in items:
        value = data[key]
        if not value:
            continue
        if up is None:
            up = '%s=%s' % (key, value)
        else:
            up += '&%s=%s' % (key, value)
    return up

def dict_to_xml(data):
    xml = '<xml>'
    for key, value in data.items():
        xml += '<%s>%s</%s>' % (key, value, key)
    xml += '</xml>'
    return xml

def xml_to_dict(data):
    dt = {}
    root = ET.fromstring(data)
    for node in root:
        dt[node.tag] = node.text
    return dt


def md5(string):
    m = hashlib.md5()   
    m.update(string)
    return m.hexdigest()

def GetPaySign(data):
    stringA = dict_to_param(data)
    stringSignTemp = stringA + '&key=' + config.mch_secret
    print stringSignTemp
    sign = md5(stringSignTemp).upper()
    return sign

def get_pay_params(prepay_id):
    data = {}
    data['nonceStr'] = uuid.uuid1().hex 
    data['appId'] = config.app_id
    data['timeStamp'] = int(time.time())
    data['package'] = 'prepay_id=' + prepay_id
    data['signType'] = 'MD5'
    data['paySign'] = GetPaySign(data)
    data['prepay_id'] = prepay_id
    return data

def get_prepay_params(request):
    POST = json.loads(request.body)
    data = {}
    params = ['body', 'detail', 'attach', 'total_fee', 'product_id']
    for param in params:
        if param in POST:
            if type(POST[param]) is unicode:
                data[param] = POST[param].encode('utf-8', 'ignore')
            else:
                data[param] = POST[param]

    data['nonce_str'] = uuid.uuid1().hex 
    data['appid'] = config.app_id
    data['mch_id'] = config.mch_id
    data['openid'] = get_openid(POST['sess_key'])
    data['notify_url'] = config.Pay_Notify_URL
    '''
    data['device_info'] = 'WEB' 
    time_start = datetime.datetime.now()
    time_expire = time_start + datetime.timedelta(seconds = config.Pay_Time)
    data['time_start'] = time_start.strftime('%Y%m%d%H%M%S')
    data['time_expire'] = time_expire.strftime('%Y%m%d%H%M%S') 
    data['sign_type'] = 'MD5'
    data['fee_type'] = 'CNY'
    '''
    data['spbill_create_ip'] = getuip(request) 
    data['out_trade_no'] = uuid.uuid1().hex
    data['trade_type'] = 'JSAPI'
    data['sign'] = GetPaySign(data)
    return data

def http_post(url, data, trans2xml=False, decode_data=True):
    if trans2xml:
        data_encode = dict_to_xml(data)
        req = urllib2.Request(url=url, data=data_encode)
    else:
        data_encode = json.dumps(data)
        header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',"Content-Type": "application/json"}
        req = urllib2.Request(url=url, data=data_encode, headers=header_dict)
    response = urllib2.urlopen(req)
    data = response.read()
    if decode_data:
        try:
            res_data = json.loads(data)
        except:
            res_data = xml_to_dict(data)
        return res_data
    else:
        return data

def http_get(url, decode_data=True):
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    data = response.read()
    if decode_data:
        try:
            res_data = json.loads(data)
        except:
            res_data = xml_to_dict(data)
        return res_data
    else:
        return data



if __name__ == '__main__':
    '''
    while True:
        jscode = raw_input("jscode:").strip()
        print http_get(config.JSCODE_SESSION_URL + jscode)
    sess = {"openid":"123", "random":"456"}
    key = save_session(sess)
    print get_session(key)
    '''
    access_token = get_and_update_access_token()
    print access_token
    #req_data = {"scene":"1", "page":"pages/index/index"}
    req_data = {"scene":"1"}
    ret_data = http_post(config.WXACODE_URL + access_token, req_data, decode_data=False)
    with open('1.jpeg', 'wb') as f_wxcode:
        f_wxcode.write(ret_data)


ROOT_URL = "https://32845718.qcloud.la/cat_mp/"

#appid = 'wx1e2f9ad8603b6d58'
#secret = 'e2a2ef1120e914db7729a3eec6b0ebf2'
app_id = 'wx1052a7ece5dc7d3e'
app_secret = '4648c65a3b0fce50b54e2a8326a57067'

#mch_id = '92313872'
mch_id = '1497928172'
mch_secret = 'miaomiaoxinqiumiaomiaoxinqiumiao'

JSCODE_SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&grant_type=authorization_code&js_code=" % (app_id, app_secret)
UnifiedOrder_URL = "https://api.mch.weixin.qq.com/pay/unifiedorder"
Pay_Notify_URL = ROOT_URL + "pay_notify"
Pay_Time = 300


#redis params
startup_nodes = [{"host": "172.17.0.4", "port": "7000"}]
EX_TIME=300


IMAGE_ROOT='/data/plat/cat_data/'

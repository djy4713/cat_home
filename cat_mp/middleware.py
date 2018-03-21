try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x
import json
import utils
from django.http import HttpResponse

class SimpleMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            data = None 
            if not request.path.endswith('login') and not request.path.endswith('notify'):
                if request.method == 'POST':
                    POST = request.POST
                    try:
                        POST = json.loads(request.body)
                    except Exception as err:
                        pass
                    if 'sess_key' not in POST or not utils.exists_key(POST['sess_key']):
                        data = {'ret_code':-1}
                    else:
                        print 'sess_key: ', POST['sess_key']
                elif request.method == 'GET':
                    if 'sess_key' not in request.GET or not utils.exists_key(request.GET['sess_key']):
                        data = {'ret_code':-1}
                    else:
                        print 'sess_key: ', request.GET['sess_key']
                else:
                    data = {'ret_code':-2}
            if data is None:
                return None
            else:
                res = json.dumps(data, ensure_ascii=False)
                return HttpResponse(res, content_type="application/json")

        except Exception as err:
            print 'SimpleMiddleware: ', err
            return None
        


    def process_response(self, request, response):
        return response

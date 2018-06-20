
from django.conf.urls import url
import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login, name='login'),
    url(r'^save_uinfo$', views.save_uinfo, name='save_uinfo'),
    url(r'^upload$', views.upload, name='upload'),
    url(r'^upload_test$', views.upload_test, name='upload_test'),
    url(r'^get_album_list$', views.get_album_list, name='get_album_list'),
    url(r'^get_album_info$', views.get_album_info, name='get_album_info'),
    url(r'^like_album$', views.like_album, name='like_album'),
    url(r'^prepay$', views.prepay, name='prepay'),
    url(r'^pay$', views.pay, name='pay'),
    url(r'^pay_notify$', views.pay_notify, name='pay_notify'),
    url(r'^reward$', views.reward, name='reward'),
    url(r'^reward_test$', views.reward_test, name='reward_test'),
    url(r'^get_rewards$', views.get_rewards, name='get_rewards'),
    url(r'^get_wxcode$', views.get_wxcode, name='get_wxcode'),
]

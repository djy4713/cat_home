
from django.conf.urls import url
import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login, name='login'),
    url(r'^upload$', views.upload, name='upload'),
    url(r'^download$', views.download, name='download'),
    url(r'^prepay$', views.prepay, name='prepay'),
    url(r'^pay_notify$', views.pay_notify, name='pay_notify'),
]

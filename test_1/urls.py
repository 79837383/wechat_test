#coding=utf-8
#project's file
from django.conf.urls import patterns, include, url
from django.contrib import admin



urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'test_1.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^admin/', include(admin.site.urls)),
    url(r'^nuanxin/$', include('myApp.urls')),
    
    url(r'^nuanxin/create_menu/$','myApp.views.create_menu'),  #Ω‚ŒˆŒ Ã‚
    
    url(r'^nuanxin/qrcode/$', 'myApp.views.qrcode'),
    
    url(r'^nuanxin/jssdk/$', 'myApp.views.jssdk'),
    url(r'^nuanxin/pay/$', 'myApp.views.pay'),
    url(r'^nuanxin/pay_notify/$', 'myApp.views.pay_notify'),
    url(r'^nuanxin/img/$', 'myApp.views.img'),
    url(r'^nuanxin/test/$', 'myApp.views.test'),

)

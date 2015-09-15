#coding=utf-8
#app's file
from django.conf.urls import patterns, include, url
from django.contrib import admin
from myApp import views

urlpatterns = patterns('',

    url(r'^$', views.checkSignature),
    url(r'^create_menu/$',views.create_menu),
)

#encoding:utf-8
import json
from lxml import etree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import tostring
from myApp.models import Access_Token, Jsapi_Ticket
import httplib2
from myApp.config import *
from datetime import datetime
import time
from datetime import timedelta
import random
import string,types
import hashlib
import cookielib
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def parse_Xml2Dict(raw_xml):
	xmlstr = etree.fromstring(raw_xml) #tostring?
	dict_xml = {}
	for child in xmlstr:
		dict_xml[child.tag] = child.text.encode(u'UTF-8')
	return dict_xml


   
# 字典 ==》 xml格式的字符串
def parse_Dict2Xml(tag, arg_dict):
    elem = Element(tag)
    elem = Dict2Xml_step_1(elem, arg_dict)
    my_str = tostring(elem, encoding=u'UTF-8')
    return my_str

def Dict2Xml_step_1(elem, arg_dict):
    for key, val in arg_dict.items():
        child = Element(key)
        if type(val)==type({}):
            child = Dict2Xml_step_1(child, val)
        else:
            child.text = str(val)
        elem.append(child)
    return elem

'''
@csrf_exempt  
def parse_Dict2Xml(tag, d):
    elem = Element(tag)
    for key, val in d.items():
        child = Element(key)
        #if type(val) is types.DictType:
        	#child.text=str(parse_Dict2Xml('xml', val))
        	#print str(val)
        #else:
        	#child.text=str(val)
        child.text=str(val)
        elem.append(child)
    my_str = tostring(elem, encoding=u'UTF-8')
    return my_str



@csrf_exempt
def parse_Dict2Xml_child_MaGe(d):
		_m_arr = []
		for key, val in d.items():
			child = Element(key)
			child.text = str(val)
			_m_arr.append(child)
		return _m_arr
'''
@csrf_exempt
def parse_Dict2Xml_Image_Child_MaGe(d):
		_m_arr = []
		for key, val in d.items():
			child = Element(key)
			child.text = str(val)
			_m_arr.append(child)
		return _m_arr

@csrf_exempt
def parse_Dict2Xml_Recurse_Child_MaGe(d):
		_m_arr = []
		for key, val in d.items():
			child = Element(key)
			if type(val) is types.StringType:
				child.text = str(val)
			elif type(val) is types.DictType:
				child_arr = parse_Dict2Xml_child_MaGe(val)
				for child_elem in child_arr:
					child.append(child_elem)
			_m_arr.append(child)
			
		return _m_arr
    
@csrf_exempt  
def parse_Dict2Xml_MaGe(tag, d):
	elem = Element(tag)
	for key, val in d.items():
		child = Element(key)
		if type(val) is types.StringType:
			child.text = str(val)
		elif type(val) is types.DictType:
			#child_arr = parse_Dict2Xml_Recurse_Child_MaGe(val)
			child_arr = parse_Dict2Xml_child_MaGe(val)
			for child_elem in child_arr:
				child.append(child_elem);
				print child
		elem.append(child)
	my_str = tostring(elem, encoding=u'UTF-8')
	return my_str


@csrf_exempt
def parse_Dict2Json(my_dict):
    my_json = json.dumps(my_dict, ensure_ascii=False)
    return my_json

@csrf_exempt  
def my_post(url, data):
    h = httplib2.Http()
    resp, content = h.request(url, 'POST', data)
    #resp会现实返回头信息
    #content 会显示”url“的相关内容。
    return resp, content
    
def my_get(url):
    h = httplib2.Http()   #获取HTTP对象
    resp, content = h.request(url, 'GET')
    return resp, content

@csrf_exempt 
def parse_Json2Dict(my_json):
    my_dict = json.loads(my_json)
    return my_dict
    
    
@csrf_exempt 
def get_access_token():
	#print "get_access_token111111111"
	try:
		token = Access_Token.objects.get(id = 1) #从数据库获取access_token
		#print "get_access_token111111222222"
	except Access_Token.DoesNotExist:
		#print "get_access_token222222222222"
		resp, result = my_get(WEIXIN_ACCESS_TOKEN_URL)
		#print "get_access_token33333333333"
		#print result
		
		decodejson = parse_Json2Dict(result)  #微信会返回下述JSON数据包
		#print "parse_Json2Dict"
		at = Access_Token(token=decodejson['access_token'],expires_in=decodejson['expires_in'],date=datetime.now())
		at.save()
		#print "get_access_token44444444444444"
		return str(decodejson['access_token'])
	#else:
	#print "get_access_token55555555555"
	if ((datetime.now() - token.date ).seconds > (token.expires_in-300)):
		#print "get_access_token55555566666"
		resp, result = my_get(WEIXIN_ACCESS_TOKEN_URL)
		#print "get_access_token6666666666666666"
		decodejson = parse_Json2Dict(result)
		#print "get_access_token7777777777777777777"
		Access_Token.objects.filter(id = 1).update(token = decodejson['access_token'],expires_in=decodejson['expires_in'],date=datetime.now())
		#print "get_access_token888888888888888"
		return str(decodejson['access_token'])
	else:
		#print "get_access_token99999999999"
		return str(token.token)
   
@csrf_exempt         
def send_text(touser, content):
	print 1111
	ACCESS_TOKEN = get_access_token()
	print 222
	post_url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=' + ACCESS_TOKEN  #发送客服消息
	post_dict = {}
	post_dict['touser'] = touser
	post_dict['msgtype'] = "text"
	text_dict = {}
	text_dict['content'] = content
	post_dict['text'] = text_dict
	post_data = parse_Dict2Json(post_dict)
	my_post(post_url, post_data)
	
def send_image(dict_str):
	res_dict = {}
	res_dict['ToUserName'] = dict_str['FromUserName']
	res_dict['FromUserName'] = dict_str['ToUserName']
	res_dict['CreateTime'] = int(time.time())
	res_dict['MsgType'] = 'image'
	res_dict['Image'] = {'MediaId':dict_str['MediaId']}
	#res_dict['Image'] = {'MediaId':'bddOrUoyXCniUmmzfzOmKGwMnyKaJSHTNa30_E97ZmI'}
	print res_dict
	echostr = parse_Dict2Xml('xml', res_dict)
	print "##############",echostr,"#############"
	print type(echostr)
	return echostr
	#print "send_image"
	#print get_access_token()
	'''
	#sendinfo = parse_Dict2Xml('xml', dict_str)
	
	
	
	#ss = '\<MediaId\>'+dict_str['MsgId']+'\<\/MediaId\>'
	#print "***********"
	#print ss
	ss = {'MediaId':"<![CDATA["+dict_str['MsgId']+"]]>",}
	#ss = parse_Dict2Xml('xml', s)
	#print '111', dict_str['FromUserName']
	data = {
		'ToUserName':"<![CDATA["+dict_str['FromUserName']+"]]>",
		'FromUserName':"<![CDATA["+dict_str['ToUserName']+"]]>",
		'CreateTime':str(int(time.time())),
		'MsgType':"<![CDATA[image]]>",
		'Image':ss,
	}

	sendinfo = parse_Dict2Xml_MaGe('xml', data)
	
	#sendinfo = "<?xml version='1.0' encoding='UTF-8'?>\n<xml><MsgType><![CDATA[image]]></MsgType><Image><MediaId><![CDATA[6194180574429926138]]></MediaId></Image><FromUserName><![CDATA[gh_9bbaac156eb7]]></FromUserName><ToUserName><![CDATA[obOsUs14Pwd4FJOru9_BiRztFkEA]]></ToUserName><CreateTime>1442078724</CreateTime></xml>"
	sendinfo = "<?xml version='1.0' encoding='UTF-8'?>\n<xml><MsgType><![CDATA[image]]></MsgType><Image><MediaId><![CDATA[6194180574429926138]]></MediaId></Image><FromUserName><![CDATA[gh_9bbaac156eb7]]></FromUserName><ToUserName><![CDATA[obOsUs14Pwd4FJOru9_BiRztFkEA]]></ToUserName><CreateTime>1442078724</CreateTime></xml>"
	'''
	
	'''
	data = {
		'ToUserName':dict_str['FromUserName'],
		'FromUserName':dict_str['ToUserName'],
		'CreateTime':int(time.time()),
		'MsgType':"image",
		'Image':{'MediaId':'bddOrUoyXCniUmmzfzOmKGwMnyKaJSHTNa30_E97ZmI',},
	}
	'''
	
	data = {
		'ToUserName':dict_str['FromUserName'],
		'FromUserName':dict_str['ToUserName'],
		'CreateTime':int(time.time()),
		'MsgType':"text",
		'Content':'aaa',
	}
	print '000'
	res = parse_Dict2Xml('xml', data)
	print res
	
	
	# sss = '''<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%d</CreateTime><MsgType><![CDATA[image]]></MsgType><Image><MediaId><![CDATA[%s]]></MediaId></Image></xml>'''

	# sendinfo = sss % (dict_str['FromUserName'],dict_str['ToUserName'],1442196978,dict_str['MsgId'])
	# print sendinfo
	# print type(sendinfo)
	# sendinfo = sendinfo.decode()
	#print type(sendinfo)
	#sendinfo = "<xml>"+dict_str['FromUserName']+"</xml>"
	#print sendinfo
	#print sendinfo
	#print dict_str['FromUserName']
	#print type(sendinfo)
	
	#str_time = str(int(time.time()))
	#sendinfo = "<xml><ToUserName>"+dict_str['FromUserName']+"</ToUserName><FromUserName>"+dict_str['ToUserName']+"</FromUserName><CreateTime>"+str_time+"</CreateTime><MsgType>image</MsgType><Image><MediaId>"+dict_str['MsgId']+"</MediaId></Image></xml>"	
		
	return HttpResponse(res)
	
@csrf_exempt
def get_user_info(openid):  #返回字典类型的用户信息
  ACCESS_TOKEN = get_access_token()
  resp, content = my_get('https://api.weixin.qq.com/cgi-bin/user/info?access_token='+ACCESS_TOKEN+'&openid='+openid+'&lang=zh_CN')
  return parse_Json2Dict(content)  #获取用户基本信息（包括UnionID机制）
  
def my_create_menu(menu_data):
	print "craete_menu begin"
	ACCESS_TOKEN = get_access_token()
	print "craete_menu 11111" 
	post_url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=' + ACCESS_TOKEN
	post_data = parse_Dict2Json(menu_data)
	print "craete_menu 22222" 
	resp, content = my_post(post_url, post_data)
	print "craete_menu 33333" 
	return parse_Json2Dict(content)
	
def create_nonce_str():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

def create_timestamp():
    return int(time.time())

def get_jsapi_ticket():
    try:
        ticket = Jsapi_Ticket.objects.get(id = 1)
    except Jsapi_Ticket.DoesNotExist:
        ACCESS_TOKEN = get_access_token()
        get_url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=' + ACCESS_TOKEN + '&type=jsapi'
        resp, result = my_get(get_url)
        decodejson = parse_Json2Dict(result)
        at = Jsapi_Ticket(ticket=decodejson['ticket'],expires_in=decodejson['expires_in'],date=datetime.now())
        at.save()
        return str(decodejson['ticket'])
    else:
        if (datetime.now() - ticket.date ).seconds > (ticket.expires_in-300):
            ACCESS_TOKEN = get_access_token()
            get_url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=' + ACCESS_TOKEN + '&type=jsapi'
            resp, result = my_get(get_url)
            decodejson = parse_Json2Dict(result)
            Jsapi_Ticket.objects.filter(id = 1).update(ticket = decodejson['ticket'],expires_in=decodejson['expires_in'],date=datetime.now())
            return str(decodejson['ticket'])
        else:
            return str(ticket.ticket)
              
def get_jsapi_signature(noncestr, timestamp, url):
    jsapi_ticket = get_jsapi_ticket()
    data = {
        'jsapi_ticket': jsapi_ticket,
        'noncestr': noncestr,
        'timestamp': timestamp,
        'url': url,
    }
    keys = data.keys()
    keys.sort()
    data_str = '&'.join(['%s=%s' % (key, data[key]) for key in keys])
    signature = hashlib.sha1(data_str.encode('utf-8')).hexdigest()
    return signature
    
def get_user_real_ip(request):
    if request.META.has_key('HTTP_X_REAL_IP'):  
        return request.META['HTTP_X_REAL_IP']  
    else:  
        return request.META['REMOTE_ADDR']  

def get_unified_order(body, total_fee, spbill_create_ip, openid):
    '''
    appid :公众账号ID(在config中设置)
    mch_id :商户号(在config中设置)
    nonce_str :随机字符串
    sign :签名
    body :商品描述
    out_trade_no :商户订单号
    total_fee :总金额
    spbill_create_ip :终端IP
    notify_url :通知地址(在config中设置)
    trade_type :交易类型(JSAPI)
    openid :用户标识
    '''
    data = {
        'appid': WEIXIN_APPID,
        'mch_id': WEIXIN_MCH_ID,
        'nonce_str': create_nonce_str(),
        'out_trade_no': create_out_trade_no(),
        'notify_url': WEIXIN_PAY_NOTIFY_URL,
        'body': body,
        'total_fee': total_fee,
        'spbill_create_ip': spbill_create_ip,
        'trade_type': 'JSAPI',
        'openid': openid,
    }
    keys = data.keys()
    keys.sort()
    data_str = '&'.join(['%s=%s' % (key, data[key]) for key in keys])
    data_str = data_str + '&key=' + WEIXIN_API_KEY
    sign = md5(str(data_str)).upper()
    data.update({'sign':sign})
    post_data = parse_Dict2Xml('xml', data)
    post_url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
    res, content = my_post(post_url, post_data)
    my_dict = parse_Xml2Dict(content)
    if my_dict['return_code'] == 'FAIL':
        print 'err: 统一下单失败!'
        return my_dict['return_msg']
    return my_dict

def create_out_trade_no():
    return str(int(time.time())) + str(random.randint(10000, 99999))
    
# MD5加密
def md5(str):
    import hashlib
    import types
    if type(str) is types.StringType:
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
    else:
        return ''
        
      
def parse_Json2Dict(my_json):
    my_dict = json.loads(my_json)
    return my_dict
    
#datagen, headers = multipart_encode({"media": open("/home/webdev/ma/test_1/static/upload/1.jpg"
# parse_Dict2Json({"title":"autoupload", "introduction":"autouploadvideo"})
# {"title":"autoupload", "introduction":"autouploadvideo"}

'''
  datagen, headers = multipart_encode({
    "media": open("/home/webdev/ma/test_1/static/upload/1.mp4", "rb"),
    "title": "my_title",
    "introduction": "my_introduction",
  })
'''
 
def upload_pic():
  register_openers()
  datagen, headers = multipart_encode({
    "type": "video",
    "media": open("/home/webdev/ma/test_1/static/upload/1.jpg", "rb"),
    "title": "my_title",
    "introduction": "my_introduction",
  })
  ACCESS_TOKEN = get_access_token()
  url = "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=" + ACCESS_TOKEN
  request = urllib2.Request(url, datagen, headers)
  json_pic = urllib2.urlopen(request).read()
  print json_pic
  dict_pic = parse_Json2Dict(json_pic)
  return dict_pic



def create_news(dict_str):
	tmp = upload_pic()  #封面永久ID
	print 'thumb_media_id=\t\t' + tmp['media_id']
	print 'thumb_media_url=\t' + tmp['url']
	fm_id = tmp['media_id']
	
	# print "000000000"

	content = '<!DOCTYPE html><html><body><h1>我abc</h1><p>def</p></body></html>'
  # "thumb_media_id": "6e0wjP4lBVI4Gdf7f6MHyp8N_g9rppKlnjiblkQFQ9s",
	data = {
		'articles':[{
			"title": "test1",
			"thumb_media_id": fm_id,
			"author": "xing",
			"digest": "摘要",
			"show_cover_pic": 0,
			"content": content,
			"content_source_url": "www.baidu.com",
		  },
		]
	}
	# print "11111111"
	# print data
	json_data = parse_Dict2Json(data)
	# print "222222222222"
	# print json_data
	ACCESS_TOKEN = get_access_token()
	# print "333333333"
	url_news = "https://api.weixin.qq.com/cgi-bin/material/add_news?access_token="+ACCESS_TOKEN
	# print type(json_data)
	# print json_data
	resp, content = my_post(url_news, json_data)
	# print "444444444"
	dict_data = parse_Json2Dict(content)
	
	print '图文素材id=\t\t' + dict_data["media_id"]
	
	
	dd = {"media_id":dict_data["media_id"],}
	json_dd = parse_Dict2Json(dd)
	url = "https://api.weixin.qq.com/cgi-bin/material/get_material?access_token="+ACCESS_TOKEN
	resp, content = my_post(url, json_dd)
	print "调用 获取永久素材接口。返回值："
	dict_cc = parse_Json2Dict(content)
	print dict_cc
	
	
	dict_c = dict_cc['news_item'][0]
	'''
	print "121212121",dict_c
	print "******************0000",dict_str
	print dict_str['FromUserName'],"+++",dict_str['ToUserName'],"+++"
	print type(dict_c['title'])
	print "+++",dict_c['digest'],"+++",dict_c['url']
	'''
	#'Title':dict_c['title'],
	
	
	dict_data_tmp = {
	'ToUserName':dict_str['FromUserName'],
	'FromUserName':dict_str['ToUserName'],
	'CreateTime':int(time.time()),
	'MsgType':"news",
	'ArticleCount':1,
	'Articles':{
		'item':{
			'Title':"titleaaaaaaaaa",
			'Description':'从某种意义上说，个人简介的写作不亚于参加面试。通过短短数百字的个人简介，不但要能较充分地展现出毕业生的才能及综合素质，而且要使聘任者感到自己是位思维清晰、条理性强、语言表达能力突出的应聘者。因此，写好个人简介是求职成功的第一步。 但是，在实际中，不少毕业生对个人简介和求职信之间的界线辨析不清，影向了求职效果。这里，我就先讲一下两者的区别与联系。',
			'Url':dict_c['url'],
			}
		}
	}
	print "hhhhhhhhhh"
	
	res_tmp = parse_Dict2Xml('xml', dict_data_tmp)
	print res_tmp
	return res_tmp
	
	
#encoding:utf-8
from django.shortcuts import render
from django.http import HttpResponse
from myApp.config import *
from myApp.myFunction import *
import hashlib
import json
from lxml import etree
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
import httplib2
from urllib import urlencode
import time
import urllib2


import sys



default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

# Create your views here.
@csrf_exempt
def checkSignature(request):  #签名验证
	if request.method == "GET":
		signature = request.GET.get("signature", None)
		timestamp = request.GET.get("timestamp", None)
		nonce = request.GET.get("nonce", None)
		echostr = request.GET.get("echostr", None)
		token = WEIXIN_TOKEN
		tmp_list = [token, timestamp, nonce]
		tmp_list.sort()
		tmp_str = "%s%s%s" % tuple(tmp_list)
		tmp_str = hashlib.sha1(tmp_str).hexdigest()
		if tmp_str == signature:
			return HttpResponse(echostr)
		else:
			return HttpResponse("weixin index")
	else:
		recv_xml = request.body.decode(u'UTF-8')
		# print "****************"
		# print recv_xml
		# print "****************"
		dict_str = parse_Xml2Dict(recv_xml)
		try:
			MsgType = dict_str['MsgType']
		except:
			MsgType = ''
		try:
			Event = dict_str['Event']  #公众号事件
		except:
			Event = ''
		# print MsgType
		if MsgType == 'text':
			res_dict = {}
			res_dict['ToUserName'] = dict_str['FromUserName']
			res_dict['FromUserName'] = dict_str['ToUserName']
			res_dict['CreateTime'] = int(time.time())
			res_dict['MsgType'] = 'text'
			
			if dict_str['Content']=='ip':
				res = create_news(dict_str)
				print "finish"
				return HttpResponse(res)
				
				ACCESS_TOKEN = get_access_token()
				print "get access_token ok"
				GET_SERVERIP_URL = 'https://api.weixin.qq.com/cgi-bin/getcallbackip?access_token='+ACCESS_TOKEN
				resp, result_ip = my_get(GET_SERVERIP_URL)
				print "get ip ok"
				dict_ip = parse_Json2Dict(result_ip)
				res_dict['Content'] = dict_ip['ip_list']
			elif dict_str['Content']=='音乐':
				print "upload_pic-----------"
				upload_pic()
				return HttpResponse("")
				
				res_dict = {
					'ToUserName':dict_str['FromUserName'],
					'FromUserName':dict_str['ToUserName'],
					'CreateTime':int(time.time()),
					'MsgType':"music",
					'Music':{'Title':"",
							'Description':"",
							'MusicUrl':"",
							'HQMusicUrl':"",
							'ThumbMediaId':"",
						},
				}
				
			elif dict_str['Content']=='图文':
				res_dict = {
					'ToUserName':dict_str['FromUserName'],
					'FromUserName':dict_str['ToUserName'],
					'CreateTime':int(time.time()),
					'MsgType':"news",
					'ArticleCount':1,
					'Articles':{
						'item':{
							'Title':"titleaaaaaaaaa",
							'Description':'从某种意义上说，个人简介的写作不亚于参加面试。通过短短数百字的个人简介，不但要能较充分地展现出毕业生的才能及综合素质，而且要使聘任者感到自己是位思维清晰、条理性强、语言表达能力突出的应聘者。因此，写好个人简介是求职成功的第一步。 但是，在实际中，不少毕业生对个人简介和求职信之间的界线辨析不清，影向了求职效果。这里，我就先讲一下两者的区别与联系。',
							'Url':"www.baidu.com",
						}
					}
				}
				print "hhhhhhhhhh"
	
				
			else:
				print "access_token----",get_access_token()
				res_dict['Content'] = dict_str['Content']
			print res_dict
			echostr = parse_Dict2Xml('xml', res_dict)
			print "##############",echostr,"#############"
			print type(echostr)
			return HttpResponse(echostr)
		elif MsgType == 'image':  #接收图片回复图片
			print "image"
			'''保存用户上传的图片
			dict_user_info = get_user_info(dict_str['FromUserName'])
			resp,content = my_get(dict_str['PicUrl'])
			filename = '/home/webdev/ma/test_1/static/upload/'+dict_user_info['nickname'].encode('utf-8')+'/'+my_get(dict_str['MediaId'])
			print filename
			print "**************************"
			if resp['status'] == '200':  
				with open(filename, 'wb') as f:  
					f.write(content)  
			
			#resp, content = my_get(dict_str['PicUrl'])
			'''
			res = send_image(dict_str)
			return HttpResponse(res)
			#send_text(dict_str['FromUserName'], "images")  
			#return HttpResponse('')
		elif MsgType == 'voice':
			dict_user_info = get_user_info(dict_str['FromUserName'])  #openid
			print '------------------------------'
			print '发送语音的用户信息如下'
			print dict_user_info
			print dict_user_info['nickname'].encode('utf-8')
			print '------------------------------'
			
			#aa = '''<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>12345678</CreateTime><MsgType><![CDATA[voice]]></MsgType><Voice><MediaId><![CDATA[%s]]></MediaId></Voice></xml>'''
			
			#aa = aa % (dict_str['FromUserName'],dict_str['ToUserName'],dict_str['MsgId'])
			
			dict_voice = {
				'ToUserName':dict_str['FromUserName'],
				'FromUserName':dict_str['ToUserName'],
				'CreateTime':int(time.time()),
				'MsgType':"voice",
				'Voice':{'MediaId':dict_str['MediaId']},
			}
			
			xml_voice = parse_Dict2Xml('xml', dict_voice)
			return HttpResponse(xml_voice)
		elif MsgType == 'video' or MsgType == 'shortvideo':
			dict_video = {
				'ToUserName':dict_str['FromUserName'],
				'FromUserName':dict_str['ToUserName'],
				'CreateTime':int(time.time()),
				'MsgType':"video",
				'Video':{
				  'MediaId':"ITSTVvhYbKR3dRWjeEzhHnB6c8_QzpU8KFwuB-SJB8U",
				},
			}
			xml_video = parse_Dict2Xml('xml', dict_video)
			print xml_video
			
			return HttpResponse(xml_video)
		elif MsgType == 'shortvideoaa':
			'''
			res_dict = {}
			res_dict['ToUserName'] = dict_str['FromUserName']
			res_dict['FromUserName'] = dict_str['ToUserName']
			res_dict['CreateTime'] = int(time.time())
			res_dict['MsgType'] = 'text'
			res_dict['Content'] = "小视频消息"
			echostr = parse_Dict2Xml('xml', res_dict)
			return HttpResponse(echostr)
			'MediaId':"ITSTVvhYbKR3dRWjeEzhHnB6c8_QzpU8KFwuB-SJB8U",
			'''
			print "shortvideo"
			print dict_str['FromUserName']
			print "MediaId-------------",dict_str['MediaId']
			dict_video = {
				'ToUserName':dict_str['FromUserName'],
				'FromUserName':dict_str['ToUserName'],
				'CreateTime':int(time.time()),
				'MsgType':"video",
				'Video':{
				  'MediaId':dict_str['MediaId'],
				},
			}
			xml_video = parse_Dict2Xml('xml', dict_video)
			print xml_video
			
			return HttpResponse(xml_video)
		elif MsgType == 'location':

			content = "消息类型:%s\n维度:%s\n经度:%s\n地图缩放大小:%s\n地理位置信息:%s\n本次消息id:%s\n" \
				%(dict_str['MsgType'],dict_str['Location_X'],dict_str['Location_Y'],dict_str['Scale'],dict_str['Label'],dict_str['MsgId'])
			print content
			res_dict = {}
			res_dict['ToUserName'] = dict_str['FromUserName']
			res_dict['FromUserName'] = dict_str['ToUserName']
			res_dict['CreateTime'] = int(time.time())
			res_dict['MsgType'] = 'text'
			res_dict['Content'] = content
			print "22222222222"
			echostr = parse_Dict2Xml('xml', res_dict)
			return HttpResponse(echostr)
		
		elif MsgType == 'link':
			content = '标题：%s\n描述：%s\n链接：%s\n' %(dict_str['Title'],dict_str['Description'],dict_str['Url'])
			dict_link = {
				'ToUserName':dict_str['FromUserName'],
				'FromUserName':dict_str['ToUserName'],
				'CreateTime':int(time.time()),
				'MsgType':"text",
				'Content':content,
			}
			echostr = parse_Dict2Xml('xml', dict_link)
			return HttpResponse(echostr)
			
		elif Event == 'subscribe':# 关注公众号事件
			content = ''
			dict_res = {
				'ToUserName':dict_str['FromUserName'],
				'FromUserName':dict_str['ToUserName'],
				'CreateTime':int(time.time()),
				'MsgType':"text",
				'Content':content,
			}
			
			print "subscribe"
			if dict_str['EventKey'] and dict_str['Ticket']:# 通过扫描二维码进行关注
				qrcode_num = dict_str['EventKey'].split('_')[1]  #事件KEY值，qrscene_为前缀，后面为二维码的参数值
				content = "感谢您关注公众号！qrcode is " + str(qrcode_num)
				#send_text(dict_str['FromUserName'], "感谢您关注公众号！qrcode is " + str(qrcode_num))
			else:
				content = "感谢您关注公众号！"
				#send_text(dict_str['FromUserName'], "感谢您关注公众号！")
			echostr = parse_Dict2Xml('xml', dict_res)
			return HttpResponse(echostr)
		elif Event == 'unsubscribe':
			print "取消关注"
			return HttpResponse('')
			
		elif Event == 'SCAN':

			dict_res = {
				'ToUserName':dict_str['FromUserName'],
				'FromUserName':dict_str['ToUserName'],
				'CreateTime':int(time.time()),
				'MsgType':"text",
				'Content':"已经关注，感谢您关注公众号！",
			}
			#send_text(dict_str['FromUserName'], "已经关注，感谢您关注公众号！")

			echostr = parse_Dict2Xml('xml', dict_res)
			return HttpResponse(echostr)
		elif Event == 'LOCATION':
			print dict_str
			print "进入会话，接收位置信息"
			
			content = "您的地理位置:\n维度:%s\n经度:%s\n精度:%s\n" \
				%(dict_str['Latitude'],dict_str['Longitude'],dict_str['Precision'])
			print content
			res_dict = {}
			res_dict['ToUserName'] = dict_str['FromUserName']
			res_dict['FromUserName'] = dict_str['ToUserName']
			res_dict['CreateTime'] = int(time.time())
			res_dict['MsgType'] = 'text'
			res_dict['Content'] = content

			echostr = parse_Dict2Xml('xml', res_dict)
			return HttpResponse(echostr)
		
		elif Event == 'CLICK':
			content = "您点击了click类型按钮key为："+dict_str['EventKey']
			dict_res = {
				'ToUserName':dict_str['FromUserName'],
				'FromUserName':dict_str['ToUserName'],
				'CreateTime':int(time.time()),
				'MsgType':"text",
				'Content':content,
			}
			echostr = parse_Dict2Xml('xml', dict_res)
			return HttpResponse(echostr)

		elif Event == 'VIEW':
			print "用户点击了view类型按钮url为："+dict_str['EventKey']
			return HttpResponse('')
		else:
			print Event
			print 1111111111
			return HttpResponse("")

def create_menu(request):
	menu_data = {}
	button1 = {}
	button21 = {}
	button22 = {}
	button2 = {}
	button3 = {}
	button1['name'] = 'click'
	button1['type'] = 'click'
	button1['key'] = 'first'
	#button1['url'] = 'http://www.xingwenpeng/nuanxin/test.html/'
	
	button21['name'] = 'view'
	button21['type'] = 'view'
	button21['key'] = 'second_one'
	button21['url'] = 'https://www.baidu.com'
	
	button22['name'] = 'view'
	button22['type'] = 'view'
	button22['key'] = 'second_two'
	button22['url'] = 'https://www.baidu.com'
	
	
	button2['name'] = 'click'
	button2['key'] = 'second'
	button2['sub_button'] = [button21,button22]

	
	button3['name'] = 'user'
	button3['type'] = 'view'
	button3['key'] = 'third'
	button3['url'] = 'https://www.baidu.com'
	
	menu_data['button'] = [button1,button2,button3]
	print menu_data
	response = my_create_menu(menu_data)
	if response['errcode'] == 0:
		return HttpResponse('create menu OK.')
	else:
		return HttpResponse('create menu err:' + response['errmsg'])
		
def my_create_qrcode(data):
    ACCESS_TOKEN = get_access_token()
    post_url = 'https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=' + ACCESS_TOKEN
    post_data = parse_Dict2Json(data)
    resp, content = my_post(post_url, post_data)
    return parse_Json2Dict(content)
    
def qrcode(request):
    value_number = request.GET.get('num', None)
    if not value_number:
        return HttpResponse('<h1>你需要在网址的后面加上num参数。如：...?num=1</h1>')
    data = {"action_name": "QR_LIMIT_SCENE", "action_info": {"scene": {"scene_id": value_number}}}
    my_dict = my_create_qrcode(data)
    my_dict['num'] = value_number
    return render(request, 'nuanxin/qrcode.html', my_dict)
    
    



def jssdk(request):
    noncestr = create_nonce_str()
    timestamp = create_timestamp()
    url = 'http://www.xingwenpeng.com' + request.get_full_path()  #request.get_host()
    print request.get_host()
    print url
    signature = get_jsapi_signature(noncestr, timestamp, url)
    my_dict = {
        'appId': WEIXIN_APPID,
        'nonceStr': noncestr,
        'timestamp': timestamp,
        'signature': signature,
    }
    return render(request, 'nuanxin/jssdk.html', my_dict)
    

        

def pay(request):
    body = '联合国定制版iPhone，全球限量10台！'
    total_fee = 123 #单位是分
    spbill_create_ip = get_user_real_ip(request)
    openid = request.GET.get('openi', '')
    my_dict = get_unified_order(body, total_fee, spbill_create_ip, openid)
    res_dict = {
        'timeStamp': str(int(time.time())),
        'nonceStr': create_nonce_str(),
        'package': 'prepay_id=' + str(my_dict['prepay_id']),
        'signType': 'MD5'
    }
    keys = res_dict.keys()
    keys.sort()
    data_str = '&'.join(['%s=%s' % (key, res_dict[key]) for key in keys])
    data_str = data_str + '&key=' + WEIXIN_API_KEY
    paySign = md5(str(data_str)).upper()
    res_dict.update({ 'paySign':paySign })
    res = parse_Dict2Json(res_dict)
    return HttpResponse(res)

def pay_notify(request):
    my_dict = parse_Xml2Dict(request.body)
    print my_dict
    return HttpResponse('<xml><return_code>SUCCESS</return_code></xml>')

def img(request):
    noncestr = create_nonce_str()
    timestamp = create_timestamp()
    url = 'http://www.xingwenpeng.com' + request.get_full_path()  #request.get_host()
    print url
    signature = get_jsapi_signature(noncestr, timestamp, url)
    my_dict = {
        'appId': WEIXIN_APPID,
        'nonceStr': noncestr,
        'timestamp': timestamp,
        'signature': signature,
    }
    return render(request, 'nuanxin/img.html', my_dict)
    
    
def test(request):
	noncestr = create_nonce_str()
	timestamp = create_timestamp()
	url = url = 'http://www.xingwenpeng.com' + request.get_full_path()
	signature = get_jsapi_signature(noncestr, timestamp, url)
	my_dict = {
		'appId': WEIXIN_APPID,
		'nonceStr': noncestr,
		'timestamp': timestamp,
		'signature': signature,
	}
	return render(request, 'nuanxin/test.html', my_dict)
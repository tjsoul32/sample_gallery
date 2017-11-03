#coding:utf-8

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from django.db.models import F, Q
from .models import ImageName as IN
from .models import ImagePath as IP
from .models import ImageTag as ITA
from .models import ImageType as ITY

from PIL import Image as Img

from django.views.decorators.csrf import csrf_exempt, csrf_protect

import os
import time, datetime
import datetime
import uuid
import hashlib
import json


MODELS = ["test1", "test2", "test3", "test4", "test5", "test6", "test7", "test8", "test9"]
#MODELS = ["test2", "test3"]


@csrf_exempt
def get_imgs(request):
    getData = request.GET.dict()
    lastid = int(getData["lastid"])
    rangetime = getData["rangetime"].strip()

    #tags = getData["tags"].strip().split(',')
    #tags = [ ',' + t + ',' for t in tags if t ] 
    #tp = getData["type"]

    tags = [',1,']
    tp = 'a'
    tp = getData["type"]

    filter_dict = {}
    if lastid > 0:
        filter_dict["id__lt"] = lastid
    if rangetime:
        rt = rangetime.split("to")    
        st = rt[0].strip()
        et = rt[1].strip()
        et = (datetime.datetime.strptime(et, "%Y-%m-%d") + datetime.timedelta(days = 1)).strftime("%Y-%m-%d")
        filter_dict["create_time__range"] = (st, et)
    if tp:
        filter_dict["type__exact"] = tp

    q = Q()
    if tags:
        for t in tags:
            q = q | Q(tags__contains = t)

    images = IN.objects.filter(**filter_dict).filter(q).order_by("-id")[:50]
    # print images.query

    res = [ {"id": img.id, "name": img.name, "path": str(img.md5.path), "time": str(img.create_time)} for img in images ]

    response = HttpResponse(json.dumps(res), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"

    return response
 

def status_check(path):
    file_pre = settings.BASE_DIR + "/gallery/" + path.split('.')[0]
     
    status = {}
    for m in MODELS:
      res = file_pre + '_' + m + ".png" 
      success = res + "_SUCCESS"
      failure = res + "_FAILURE"

      get_r = os.path.exists(res) 
      get_s = os.path.exists(success) 
      get_f = os.path.exists(failure) 

      s = 0
      if get_r and get_s:
          s = 1
      elif get_f and not get_r:
          s = 9
      status[m] = s

    #print status
    return status


@csrf_exempt
def get_img_stylized(request):    
    getData = request.GET
    img_id = getData["img_id"]

    try:
        img = IN.objects.get(id = img_id)
        getpath = IP.objects.get(md5 = img.md5.md5)
        img_path = str(getpath.path)
    except Exception as e:
        print e
        img_path = ''

    res = {}
    res["img_id"] = img_id
    res["img_path"] = img_path
    res["status"] = status_check(img_path)

    response = HttpResponse(json.dumps(res), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"

    return response
    

def get_tags(request):
    get_tags = ITA.objects.all().order_by("-counter")
    res = [ {"id": tag.tag_id, "name": tag.tag_name} for tag in get_tags ]

    return HttpResponse(json.dumps(res), content_type="application/json")


def get_types(request):
    get_types = ITY.objects.all()
    res = [ {"id": tp.type_id, "name": tp.type_name} for tp in get_types ]

    return HttpResponse(json.dumps(res), content_type="application/json")


@csrf_exempt
def upload_img(request):
    reqfile = request.FILES.get('picfile') #picfile要和html里面一致
    md5 = request.POST.get('md5')

    #tags = ',' + request.POST.get('tags').strip(',') + ','
    #tp = request.POST.get('type')
    tags = ',1,'
    tp = 'a'

    dir_day = time.strftime('%Y%m%d',time.localtime(time.time()))

    try:
        img = Img.open(reqfile)
        width = img.size[0]

        this_uuid = str(uuid.uuid1())
        img_name = this_uuid + "." + img.format
        img_name_200 = this_uuid + "_200." + img.format

        store_dir = settings.BASE_DIR + "/gallery/uploads/%s"%dir_day

        if not os.path.exists(store_dir):
            os.makedirs(store_dir)

        store_path = store_dir + "/%s"%img_name
        store_path_200 = store_dir + "/%s"%img_name_200

        img.save(store_path, img.format)#保存图片 
        img.thumbnail((200, 200), Img.ANTIALIAS)#对图片进行等比缩放
        img.save(store_path_200, img.format)#缩略图
    
        path = "uploads/%s/%s"%(dir_day, img_name)
        create_time = datetime.datetime.now()
        # print name, original, created
    
        try:    
            im = IP.objects.create(md5 = md5, path = path)
        except:
            im = IP.objects.get(md5 = md5)
    
        img = IN.objects.create(name = reqfile, md5 = im, tags = tags, type = tp, create_time = create_time)

        tags = [ t for t in tags.split(',') if t ]
        ITA.objects.filter(tag_id__in = tags).update(counter = F('counter') + 1)

        # print store_path

        for model_name in MODELS:
            #print time.strftime('%Y%m%d  %H:%M:%S',time.localtime(time.time()))
            cmd = "sh /home/hao.guo/projects/fast-neural-style/webscripts/webCall.sh %s %s %s"%(store_path, model_name, width)
            os.popen(cmd)  
           
        '''
        t = IN.objects.get(name = reqfile)
        print t.md5.path
        '''    
        img_id = img.id
        status = 1
        img_path = path
    except IOError:
        img_id = 0
        status = 0
        img_path = ''

    res = {}
    res["img_id"] = img_id
    res["status"] = status

    res["img_path"] = img_path

    response = HttpResponse(json.dumps(res), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"

    return response


@csrf_exempt
def upload_check(request):
    postData = request.POST.dict()
    name = postData["name"]
    md5 = postData["md5"]
    #tags = ',' + postData["tags"].strip(',') + ','
    #tp = postData["type"]
    tags = ',1,'
    tp = 'a'

    exist = 0
    img_path = ''
    try:
        get_md5 = IP.objects.get(md5 = md5)
        create_time = datetime.datetime.now()
        img = IN.objects.create(name = name, md5 = get_md5, tags = tags, type=tp, create_time = create_time)
        tags = [ t for t in tags.split(',') if t ]
        ITA.objects.filter(tag_id__in = tags).update(counter = F('counter') + 1)
        
        img_id = img.id
        exist = 1
        img_path = str(get_md5.path)
    except Exception as e:
        print e
        img_id = 0

    res = {}
    res["img_id"] = img_id
    res["exist"] = exist
    res["img_path"] = img_path

    response = HttpResponse(json.dumps(res), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"

    return response



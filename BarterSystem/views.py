from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext
import json
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.cache import cache_page
from BarterSystem.models import *
import datetime
from django.template.loader import render_to_string
from django.core import serializers
from itertools import chain
import boto3

# -*- coding: utf-8 -*-
# sns_client = boto3.client('sns',region_name="us-west-2")
# sqs_client = boto3.client('sqs',
#                             aws_access_key_id = '',
#                             aws_secret_access_key = '',
#                           )



# Create your views here.
def index(request):
    if 'uid' in request.session:
        del request.session['uid']
    return render(request,'index.html')

@csrf_exempt
def signin(request):
    if request.POST.get('fname'):
        print(request.POST)
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        zipcode = request.POST.get('zipcode')
        contact = request.POST.get('contact')
        if request.POST.get('profession'):
            profession = request.POST.get('profession')
        else:
            profession = None
        password = request.POST.get('password')
        user = User(fname=fname,lname=lname,email=email,age=age,gender=gender,street=street,city=city,state=state,country=country,zipcode=zipcode,contact=contact,profession=profession,password=password)
        user.save()
        # response = sqs_client.create_queue(
        #     QueueName=str(user.uid)
        # )
        # print(response)
    return render(request,'signin.html')

@csrf_exempt
def signup(request):
    return render(request,'signup.html')

@csrf_exempt
def ref(request):
    print(request.POST)
    return render(request, 'homepage.html')

@csrf_exempt
def home(request,**kwargs):
    print(request.POST)

    #return render(request, 'home.html')

    if request.POST.get('email') and 'uid' not in request.session:
        try:
            print("Password matched!!")
            user = User.objects.get(email=request.POST.get('email'),password=request.POST.get('password'))
            request.session['uid'] = user.uid
            print(request.session['uid'])
        # sqs_response = sqs_client.get_queue_url(
        #     QueueName=str(request.session['uid'])
        # )
        # sqs_queue_arn = sqs_client.get_queue_attributes(
        #     QueueUrl=sqs_response['QueueUrl'],
        #
        # )
        # print(sqs_queue_arn)
        # # response = sns_client.publish(
        #     TargetArn=sqs_response['QueueUrl'],
        #     Message="You have just logged in!"
        # )
            #posts = Post.objects.all().values_list('product_name', flat=True)
        except:
            print ("Password not matching")
            return HttpResponse("<script>alert('Invalid Credential Details');location.href='/'</script>")

    print(request.session['uid'])
    if 'uid' in request.session:

        if request.method == "POST":
            id = request.POST.get('id')
            dec = request.POST.get('dec')
            Swap.objects.filter(id = id).update(swap_status = dec)
        posts = Post.objects.all().values_list('product_name','pid','post_timestamp').order_by('-post_timestamp')
        print (posts)
        swap_Data = Swap.objects.all().values_list('sender_pid','receiver_pid','swap_status','id')
        print (swap_Data)
        session_id = request.session['uid']
        prod_list = []
        for j,i,k,x in swap_Data:
            #print i
            receiver_details = Post.objects.get(pid = int(i))
            pending_prod = dict()
            pending_prod['pid'] = receiver_details.pid
            pending_prod['swap_status'] = k
            print ("see")
            print (receiver_details.posted_by_uid.uid)
            print (session_id)
            prod_list.append((j, i, k,x, receiver_details.product_name, receiver_details.posted_by_uid.uid,session_id))
        print ("success in home")
        return render(request, 'home.html', {'posts': posts,'swaps':prod_list})


@csrf_exempt
def products(request):
    if request.POST:
        p_id = request.POST.get('productid')
        print ("in products")
        print (p_id)
        product_details = Post.objects.get(pid=p_id)
        if product_details.post_status == 'A':
            status='Active'
        else:
            status='Passive'
        prod_det = json.dumps({
            'pid':int(product_details.pid),
            'product_name':str(product_details.product_name),
            'posted_by_uid':int(product_details.posted_by_uid.uid),
            'product_desc': str(product_details.product_desc),
            'product_age':int(product_details.product_age),
            'status':status,
            'estimated_price':float(product_details.estimated_price),
            'category': str(product_details.cid.cname),
        })
        return render(request,'products.html',{'productDetails':prod_det})




@csrf_exempt
def profile(request):
    if 'uid' in request.session:
        user = User.objects.get(uid=request.session['uid'])
        if request.method=="POST":

            user.fname = request.POST.get('fname')
            user.lname = request.POST.get('lname')
            user.age = request.POST.get('age')
            user.gender = request.POST.get('gender')
            user.street = request.POST.get('street')
            user.city = request.POST.get('city')
            user.state = request.POST.get('state')
            user.country = request.POST.get('country')
            user.zipcode = request.POST.get('zipcode')
            user.contact = request.POST.get('contact')
            if request.POST.get('profession'):
                user.profession = request.POST.get('profession')
            else:
                user.profession = None
            user.save()
            print("Reached")

        user_details = json.dumps({
            'fname':user.fname,
            'lname':user.lname,
            'age': user.age,
            'gender': user.gender,
            'street': user.street,
            'city': user.city,
            'state': user.state,
            'country': user.country,
            'zipcode': user.zipcode,
            'contact': user.contact,
            'profession': user.profession,
        })
        if request.method == "POST":
            return JsonResponse({"status":"success"})
        else:
            return render(request, 'profile.html',{'user':user_details})

@csrf_exempt
def post(request):
    print(request.POST)

    if request.POST.get('email') and 'uid' not in request.session:
        try:
            print("Password matched!!")
            user = User.objects.get(email=request.POST.get('email'),password=request.POST.get('password'))
            request.session['uid'] = user.uid
            #print(request.session['uid'])
        except:
            print ("Password not matching")
            return HttpResponse("<script>alert('Invalid Credential Details');location.href='/'</script>")

    print(request.session['uid'])
    if 'uid' in request.session:
        prod = ProductCategory.objects.all().values_list('cname', flat=True)
        if request.method=="POST":
            prod.cid = request.POST.get('cid')
            prod.cname = request.POST.get('cname')
            prod.save()
            print ("success")
        return render(request,'post.html', {'products': prod})


@csrf_exempt
def postin(request):
    print(request.POST)
    if request.POST:
        posted_by_uid_id = request.session['uid']
        product_name = request.POST.get('pname')
        product_desc = request.POST.get('desc')
        product_age = request.POST.get('age')
        estimated_price = request.POST.get('price')
        category = request.POST.get('categories')
        getcid = ProductCategory.objects.get(cname=category)
        cid_id = getcid.cid
        post_timestamps = datetime.datetime.now()
        post_status = 'A'
        items = Post(posted_by_uid_id = posted_by_uid_id, product_name=product_name, product_desc = product_desc, product_age = product_age, estimated_price = estimated_price,cid_id= cid_id,post_timestamp=post_timestamps,post_status=post_status)
        items.save()
        print("before call")
        mcid_id = request.POST.getlist('cats')
        #return HttpResponse("List items: %s" %mcid_id)
        print (mcid_id)
        getmcid=list()
        poster = Post.objects.all().order_by('-pid')[0]

        for i in mcid_id:
            pc = ProductCategory.objects.get(cname=i)
            swapch = SwapChoice(cid_id=pc, pid_id=poster)
            swapch.save()
            #getmcid.append(ProductCategory.objects.get(cname=i))
        print("here")
    return render(request,'home.html')

@csrf_exempt
def contact(request):
    return render(request, 'contact.html')

@csrf_exempt
def about(request):
    return render(request, 'about.html')

@csrf_exempt
def setnotifications(request):
    notification = Notification.objects.filter(uid__uid=request.session['uid'], view_status='N')
    print(notification)
    notification_list=list()

    for n in notification:
        nd = dict()
        nd['msg'] = n.notification
        nd['time']= divmod((n.notification_timestamp.replace(tzinfo=None)-datetime.datetime.now()).seconds,3600)[0]
        notification_list.append(nd)

    return JsonResponse({"status": notification_list})

@csrf_exempt
def recommendations(request):
    if 'uid' in request.session:
        print('Swap IDs',request.POST)
        if request.method == 'POST' and request.POST.get('sender_pid') and request.POST.get('receiver_pid'):
            sender_pid = Post.objects.get(pid=request.POST.get('sender_pid'))
            receiver_pid = Post.objects.get(pid=request.POST.get('receiver_pid'))
            swap = Swap(sender_pid=sender_pid,receiver_pid=receiver_pid)
            swap.save()
            notification = Notification(uid=receiver_pid.posted_by_uid,notification=(sender_pid.posted_by_uid.fname + ' sent you a swap request. Please view your pendings requests.'))
            notification.save()
            return JsonResponse({"status": "success"})

        posts = Post.objects.filter(posted_by_uid=request.session['uid'])
        post_list = dict()
        for p in posts:
            print('\n')
            print('Product ',p.product_name)
            print('Price ',p.estimated_price)
            print('Posted_by Uid ',p.posted_by_uid.uid)
            post_list[(p.pid,p.product_name)] = list()
            categories = SwapChoice.objects.filter(pid_id=p.pid)
            print('Categories',categories)

            if(len(categories)==0):
                recommended_posts = Post.objects.filter(estimated_price__range=(float(p.estimated_price)-float(50),float(p.estimated_price)+float(50)),post_status='A').exclude(posted_by_uid__uid=p.posted_by_uid.uid)
            else:
                categories_list = list()
                for c in categories:
                    categories_list.append(c.cid_id.cid)
                print(categories_list)
                recommended_posts = Post.objects.filter(
                    estimated_price__range=(float(p.estimated_price) - float(50), float(p.estimated_price) + float(50)),
                    post_status='A',cid__cid__in=categories_list).exclude(posted_by_uid__uid=p.posted_by_uid.uid)

            print('Posts ')
            for i in recommended_posts:
                try:
                    swap_data = Swap.objects.get(sender_pid__pid__in=[p.pid,i.pid],receiver_pid__pid__in=[p.pid,i.pid])
                except:
                    recommended_posts_categories = SwapChoice.objects.filter(pid_id=i.pid)

                    if (len(recommended_posts_categories) == 0):
                        print(i.product_name)
                        post_data = dict()
                        post_data['id'] = i.pid
                        post_data['name'] = i.product_name
                        post_data['desc'] = i.product_desc
                        post_data['category'] = i.cid.cname
                        post_data['posted_by'] = i.posted_by_uid.fname
                        post_list[(p.pid,p.product_name)].append(post_data)
                    else:
                        recommendations_categories_list = list()
                        for rc in recommended_posts_categories:
                            if (rc.cid_id.cid == p.cid.cid):
                                print(i.product_name)
                                post_data = dict()
                                post_data['id'] = i.pid
                                post_data['name'] = i.product_name
                                post_data['desc'] = i.product_desc
                                post_data['category'] = i.cid.cname
                                post_data['posted_by'] = i.posted_by_uid.fname
                                post_list[(p.pid,p.product_name)].append(post_data)
                                break

        print(post_list)

        return render(request, 'recommendations.html',{'recommendations': post_list})

#(?P<username>[a-zA-Z0-9]{1,})

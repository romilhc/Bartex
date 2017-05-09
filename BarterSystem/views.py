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

# -*- coding: utf-8 -*-


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

    return render(request,'signin.html')

@csrf_exempt
def signup(request):
    return render(request,'signup.html')

@csrf_exempt
def ref(request):
    print(request.POST)
    return render(request, 'homepage.html')

@csrf_exempt
def home(request):
    print(request.POST)

    #return render(request, 'home.html')

    if request.POST.get('email') and 'uid' not in request.session:
        try:
            print("Password matched!!")
            user = User.objects.get(email=request.POST.get('email'),password=request.POST.get('password'))
            request.session['uid'] = user.uid
            print(request.session['uid'])
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
            print (receiver_details.posted_by_uid_id.uid)
            print (session_id)
            prod_list.append((j, i, k,x, receiver_details.product_name, receiver_details.posted_by_uid_id.uid,session_id))
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
            'post_status':status,
            'estimated_price':float(product_details.estimated_price),
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



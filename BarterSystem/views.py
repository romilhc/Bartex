from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from BarterSystem.models import *
import datetime
import boto3
from BarterSystem.awsml import *

# -*- coding: utf-8 -*-
sns_client = boto3.client('sns',
                            aws_access_key_id = '',
                            aws_secret_access_key = '',
                                                    region_name="us-west-2")
sqs_client = boto3.client('sqs',
                            aws_access_key_id = '',
                            aws_secret_access_key = '',
                          region_name="us-west-2"
                          )


def getQueueArn(url):
    url=url[8:]
    print(url)
    tempstr = url.split('.')
    tempstr2 = tempstr.pop().split('/')

    print(tempstr2)
    finalUrl = ['arn','aws'] + tempstr + tempstr2

    return ':'.join(finalUrl)

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
        sqs_response = sqs_client.create_queue(
            QueueName=str(user.uid)
        )
        sns_response = sns_client.publish(
            PhoneNumber=user.contact,
            Message="Hi " + user.fname + ", you have just signed up on BartEx!"
        )

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
            request.session['notifications_set']=False
            print(request.session['uid'])

            # sqs_queue_arn = sqs_client.get_queue_attributes(
            #     QueueUrl=sqs_response['QueueUrl'],
            #     AttributeNames='All'
            #
            # )

            # sqs_response = sqs_client.get_queue_url(
            #     QueueName=str(user.uid)
            # )
            # print(sqs_response)
            # msg = "Hi "+user.fname+", you have just logged in to BartEx!"
            # queue_response = sqs_client.send_message(
            #     QueueUrl=sqs_response['QueueUrl'],
            #     MessageBody=json.dumps({'msg': msg, 'timestamp': str(datetime.datetime.utcnow())})
            # )
            # print(queue_response)
            # print(getQueueArn(str(sqs_response['QueueUrl'])))

            response = sns_client.publish(
                PhoneNumber=user.contact,
                Message="Hi "+user.fname+", you have just logged in to BartEx!"
            )

                #     posts = Post.objects.all().values_list('product_name', flat=True)
        except Exception as e:
            print(e)
            print ("Password not matching")
            return HttpResponse("<script>alert('Invalid Credential Details');location.href='/'</script>")

    print(request.session['uid'])
    if 'uid' in request.session:

        if request.method == "POST" and request.POST.get('id') and request.POST.get('dec'):
            id = request.POST.get('id')
            dec = request.POST.get('dec')
            Swap.objects.filter(id = id).update(swap_status = dec)

            swap = Swap.objects.get(id=id)
            print(swap)
            sqs_response = sqs_client.get_queue_url(
                QueueName=str(swap.sender_pid.posted_by_uid.uid)
            )
            print(sqs_response)
            if(dec=='A'):
                Post.objects.filter(pid__in=[swap.sender_pid.pid,swap.receiver_pid.pid]).update(post_status='P')
                msg = swap.receiver_pid.posted_by_uid.fname + ' accepted your swap request!'
                response = sns_client.publish(
                    PhoneNumber=swap.sender_pid.posted_by_uid.contact,
                    Message="Hi " + swap.sender_pid.posted_by_uid.fname + ", " + swap.receiver_pid.posted_by_uid.fname + " accepted your swap request!"
                )
            else:
                msg = swap.receiver_pid.posted_by_uid.fname + ' rejected your swap request!'

                response = sns_client.publish(
                    PhoneNumber=swap.sender_pid.posted_by_uid.contact,
                    Message="Hi " + swap.sender_pid.posted_by_uid.fname + ", " + swap.receiver_pid.posted_by_uid.fname + " rejected your swap request!"
                )

            queue_response = sqs_client.send_message(
                QueueUrl=sqs_response['QueueUrl'],
                MessageBody=json.dumps({'msg': msg, 'timestamp': str(datetime.datetime.utcnow())})
            )

            print(queue_response)
            print(getQueueArn(str(sqs_response['QueueUrl'])))

        posts = Post.objects.all().values_list('product_name','pid','post_timestamp','posted_by_uid').order_by('-post_timestamp')
        print(posts)
        posted = list()
        for i in posts:
            if(request.session['uid'] == i[3]):
                print("in loop")
                posted.append(i)
                print(posted)


        swap_Data = Swap.objects.all().values_list('sender_pid','receiver_pid','swap_status','id')
        print (swap_Data)
        session_id = request.session['uid']
        prod_list = []
        send_list =[]
        for j,i,k,x in swap_Data:
            #print i
            receiver_details = Post.objects.get(pid = int(i))
            sender_details = Post.objects.get(pid=int(j))
            pending_prod = dict()
            pending_prod['pid'] = receiver_details.pid
            pending_prod['swap_status'] = k
            print ("see")
            print (receiver_details.posted_by_uid.uid)
            print (session_id)
            prod_list.append((j, i, k,x, receiver_details.product_name, receiver_details.posted_by_uid.uid,session_id,sender_details.product_name))
            send_list.append((j,i,k,x,sender_details.product_name,sender_details.posted_by_uid.uid,session_id,receiver_details.product_name))
            print('SendList',send_list)
        print ("success in home")
        print(prod_list)
        return render(request, 'home.html', {'posts': posted,'swaps':prod_list,'trending':posts,'send':send_list})


@csrf_exempt
def products(request):

    if request.POST:
        post_comments_list=list()
        liked_post = 0
        faved_post = 0
        if request.POST.get('comment'):
            review = request.POST.get('comment')

            post_reviews = PostReviews(uid_id=request.session['uid'],pid_id=int(request.POST.get('pid')),comment=str(request.POST.get('comment')),rating=int(request.POST.get('rating')))
            post_reviews.save()

        if request.POST.get('liked_pid'):

            like_post = Like(uid_id=request.session['uid'],pid_id=int(request.POST.get('liked_pid')))
            like_post.save()

        if request.POST.get('faved_pid'):

            fav_post = Favourite(uid_id=request.session['uid'],pid_id=int(request.POST.get('faved_pid')))
            fav_post.save()

        if request.POST.get('pname'):
            posted_by_uid = request.session['uid']
            product_name = request.POST.get('pname')
            product_desc = request.POST.get('desc')
            product_age = request.POST.get('age')
            estimated_price = request.POST.get('price')
            category = request.POST.get('categories')
            record = {'Var2': product_name, 'Var3': product_desc, 'Var4': category}
            print(record)
            estimated_price = prediction(record)
            print('Estimated Price: ', estimated_price)
            getcid = ProductCategory.objects.get(cname=category)
            cid_id = getcid.cid
            post_timestamps = datetime.datetime.now()
            post_status = 'A'
            product_details = Post(posted_by_uid_id=posted_by_uid, product_name=product_name, product_desc=product_desc,
                         product_age=product_age, estimated_price=estimated_price, cid_id=cid_id,
                         post_timestamp=post_timestamps, post_status=post_status)
            product_details.save()
            mcid_id = request.POST.getlist('cats')
            pid = Post.objects.all().order_by('-pid')[0]
            for i in mcid_id:
                pc = ProductCategory.objects.get(cname=i)
                swapch = SwapChoice(cid_id=pc, pid_id=pid)
                swapch.save()
            if product_details.post_status == 'A':
                status='Active'
            else:
                status='Passive'

        else:
            pid = request.POST.get('productid')
            print ("in products")
            print (pid)

            product_details = Post.objects.get(pid=int(pid))
            if product_details.post_status == 'A':
                status='Active'
            else:
                status='Passive'
            post_comments = PostReviews.objects.filter(pid__pid=pid)

            for i in post_comments:
                if(i.uid.uid==request.session['uid']):
                    post_comments_list.append(('You', i.comment, [True] * i.rating, str(divmod((i.post_review_timestamp.replace(tzinfo=None)-datetime.datetime.now()  ).seconds,3600)[0])))
                else:
                    post_comments_list.append((i.uid.fname,i.comment,[True]*i.rating,str(divmod((i.post_review_timestamp.replace(tzinfo=None)-datetime.datetime.now()  ).seconds,3600)[0])))

            liked_post = Like.objects.filter(pid__pid=pid)
            if (len(liked_post) == 0):
                liked_post = 0
            else:
                liked_post = len(liked_post)

            faved_post = Favourite.objects.filter(pid__pid=pid)
            if (len(faved_post) == 0):
                faved_post = 0
            else:
                faved_post = len(faved_post)



        prod_det = json.dumps({
            'pid':int(product_details.pid),
            'product_name':str(product_details.product_name),
            'posted_by_uid':int(product_details.posted_by_uid.uid),
            'posted_by_fname': str(product_details.posted_by_uid.fname),
            'product_desc': str(product_details.product_desc),
            'product_age':int(product_details.product_age),
            'status':status,
            'estimated_price':float(product_details.estimated_price),
            'category': str(product_details.cid.cname),
        })



        return render(request,'products.html',{'productDetails':prod_det,'post_comments':post_comments_list,'liked_post':liked_post,'faved_post':faved_post})




@csrf_exempt
def profile(request):
    print(request.session['uid'])
    print(request.method)
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

'''
@csrf_exempt
def postin(request):
    print(request.POST)
    if request.POST:
        posted_by_uid = request.session['uid']
        product_name = request.POST.get('pname')
        product_desc = request.POST.get('desc')
        product_age = request.POST.get('age')
        estimated_price = request.POST.get('price')
        category = request.POST.get('categories')
        record = {'Var2': product_name, 'Var3': product_desc, 'Var4': category}
        print(record)
        estimated_price = prediction(record)
        print('Estimated Price: ', estimated_price)
        getcid = ProductCategory.objects.get(cname=category)
        cid_id = getcid.cid
        post_timestamps = datetime.datetime.now()
        post_status = 'A'
        items = Post(posted_by_uid_id = posted_by_uid, product_name=product_name, product_desc = product_desc, product_age = product_age, estimated_price = estimated_price,cid_id= cid_id,post_timestamp=post_timestamps,post_status=post_status)
        items.save()

        prod_det = json.dumps({
            #'pid': int(items.pid),
            'product_name': str(items.product_name),
            'posted_by_uid': int(items.posted_by_uid.uid),
            'product_desc': str(items.product_desc),
            'product_age': int(items.product_age),
            'status': str(items.post_status),
            'estimated_price': float(items.estimated_price),
            'category': str(items.cid.cname),
        })
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
            print(swapch)
            #getmcid.append(ProductCategory.objects.get(cname=i))
        print("here")
    return render(request,'products.html',{'prod':prod_det})
'''
@csrf_exempt
def contact(request):
    return render(request, 'contact.html')

@csrf_exempt
def about(request):
    return render(request, 'about.html')

@csrf_exempt
def setnotifications(request):
    # notification = Notification.objects.filter(uid__uid=request.session['uid'], view_status='N')
    # print(notification)
    notification_list=list()
    sqs_response = sqs_client.get_queue_url(
        QueueName=str(request.session['uid'])
    )
    print(sqs_response)
    while True:
        queue_response = sqs_client.receive_message(
            QueueUrl=sqs_response['QueueUrl']
        )
        if ('Messages' in queue_response):
            print(queue_response)
            nd = dict()
            received_msg=json.loads(queue_response['Messages'][0]['Body'])
            nd['msg'] = received_msg['msg']
            # print(received_msg['msg'],received_msg['timestamp'])
            # print(divmod((datetime.datetime.utcnow()-datetime.datetime.strptime(received_msg['timestamp'],"%Y-%m-%d %H:%M:%S.%f")).seconds,3600)[0])
            #nd['date'] = queue_response['ResponseMetadata']['date'].replace(tzinfo=None)--datetime.datetime.utcnow()
            nd['time']= divmod((datetime.datetime.utcnow()-datetime.datetime.strptime(received_msg['timestamp'],"%Y-%m-%d %H:%M:%S.%f")).seconds,3600)[0]
            notification_list.append(nd)
        else:
            break
    # for n in sqs_client.receive_message(QueueUrl=sqs_response['QueueUrl']):
    #     print(n)
        # nd = dict()
        # nd['msg'] = n.notification
        # nd['time']= divmod((n.notification_timestamp.replace(tzinfo=None)-datetime.datetime.now()).seconds,3600)[0]
        # notification_list.append(nd)

    if request.session['notifications_set']==False:
        request.session['notification'] = notification_list
        request.session['notifications_set']=True
        print(request.session['notification'])
        return JsonResponse({"status": notification_list})
    else:
        return JsonResponse({"status": request.session['notification']})

@csrf_exempt
def deletenotifications(request):
    try:
        sqs_response = sqs_client.get_queue_url(
            QueueName=str(request.session['uid'])
        )
        print(sqs_response)
        queue = sqs_client.purge_queue(
            QueueUrl=sqs_response['QueueUrl']
        )
        request.session['notification'] = list()
        request.session['notifications_set']=False
        return JsonResponse({"status": 'success'})
    except:
        return JsonResponse({"status": 'failure'})

@csrf_exempt
def recommendations(request):
    if 'uid' in request.session:
        print('Swap IDs',request.POST)
        if request.method == 'POST' and request.POST.get('sender_pid') and request.POST.get('receiver_pid'):
            sender_pid = Post.objects.get(pid=request.POST.get('sender_pid'))
            receiver_pid = Post.objects.get(pid=request.POST.get('receiver_pid'))
            swap = Swap(sender_pid=sender_pid,receiver_pid=receiver_pid)
            swap.save()
            sqs_response = sqs_client.get_queue_url(
                QueueName=str(receiver_pid.posted_by_uid.uid)
            )
            print(sqs_response)
            msg=sender_pid.posted_by_uid.fname + ' sent you a swap request. Please view the swap requests!'
            queue_response = sqs_client.send_message(
                QueueUrl=sqs_response['QueueUrl'],
                MessageBody=json.dumps({'msg':msg,'timestamp':str(datetime.datetime.utcnow())})
            )
            print(queue_response)
            print(getQueueArn(str(sqs_response['QueueUrl'])))
            response = sns_client.publish(
                PhoneNumber=receiver_pid.posted_by_uid.contact,
                Message="Hi " + receiver_pid.posted_by_uid.fname + ", " + sender_pid.posted_by_uid.fname + " sent you a swap request!"
            )

            # notification = Notification(uid=receiver_pid.posted_by_uid,notification=(sender_pid.posted_by_uid.fname + ' sent you a swap request. Please view your pendings requests.'))
            # notification.save()
            return JsonResponse({"status": "success"})

        posts = Post.objects.filter(posted_by_uid=request.session['uid'],post_status='A')
        post_list = dict()
        for p in posts:
            print('\n')
            print('Product ',p.product_name)
            print('Price ',p.estimated_price)
            print('Posted_by Uid ',p.posted_by_uid.uid)
            print('Post Status',p.post_status)
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

@csrf_exempt
def details(request):
    searchres = int(request.POST.get('searchresult').split(':')[0])
    print("details")
    print(searchres)
    print(request.POST.get('searchresult').split(':')[1])
    type = request.POST.get('searchresult').split(':')[1]
    if Post.objects.filter(pid=searchres).exists() and type=='P':
        product_details = Post.objects.get(pid=searchres)
        if product_details.post_status == 'A':
            status = 'Active'
        else:
            status = 'Passive'

        post_comments_list = list()
        liked_post = 0
        faved_post = 0
        post_comments = PostReviews.objects.filter(pid__pid=searchres)

        for i in post_comments:
            if (i.uid.uid == request.session['uid']):
                post_comments_list.append(('You', i.comment, [True] * i.rating, str(
                    divmod((i.post_review_timestamp.replace(tzinfo=None) - datetime.datetime.now()).seconds, 3600)[0])))
            else:
                post_comments_list.append((i.uid.fname, i.comment, [True] * i.rating, str(
                    divmod((i.post_review_timestamp.replace(tzinfo=None) - datetime.datetime.now()).seconds, 3600)[0])))

        liked_post = Like.objects.filter(pid__pid=searchres)
        if (len(liked_post) == 0):
            liked_post = 0
        else:
            liked_post = len(liked_post)

        faved_post = Favourite.objects.filter(pid__pid=searchres)
        if (len(faved_post) == 0):
            faved_post = 0
        else:
            faved_post = len(faved_post)

        prod_det = json.dumps({
            'pid': int(product_details.pid),
            'product_name': str(product_details.product_name),
            'posted_by_uid': int(product_details.posted_by_uid.uid),
            'posted_by_fname': str(product_details.posted_by_uid.fname),
            'product_desc': str(product_details.product_desc),
            'product_age': int(product_details.product_age),
            'status': status,
            'estimated_price': float(product_details.estimated_price),
            'category': str(product_details.cid.cname),
        })
        return render(request, 'products.html',
                      {'productDetails': prod_det, 'post_comments': post_comments_list, 'liked_post': liked_post,
                       'faved_post': faved_post})

    elif User.objects.filter(uid=searchres).exists()  and type=='U':
        user_det = User.objects.get(uid=searchres)
        print(user_det)
        user_details = json.dumps({
            'fname': str(user_det.fname),
            'lname': user_det.lname,
            'age': user_det.age,
            'gender': user_det.gender,
            'street': user_det.street,
            'city': user_det.city,
            'state': user_det.state,
            'country': user_det.country,
            'zipcode': user_det.zipcode,
            'contact': user_det.contact,
            'profession': user_det.profession,
        })
        return render(request, 'userprofile.html', {'user': user_details})

@csrf_exempt
def search(request):
    if request.method == "POST":
        name = request.POST.get('searching')
        # print User.objects.get(fname=name)
        if User.objects.filter(fname=name).exists():
            users = User.objects.filter(fname=name)
            print(users)
            users_list = list()
            for p in users:
                users_list.append((p.uid, p.fname,'U'))
            return render(request, 'search.html',{'results':users_list})
        elif Post.objects.filter(product_name=name).exists():
            posts = Post.objects.filter(product_name=name)
            print(posts)
            posts_list = list()
            for p in posts:
                posts_list.append((p.pid,p.product_name,'P'))
            return render(request,'search.html',{'results':posts_list})
        else:
            return HttpResponse("No item found")

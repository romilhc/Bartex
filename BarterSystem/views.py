from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext
import json
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.cache import cache_page
from BarterSystem.models import *


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
        except:
            print ("Password not matching")
            return HttpResponse("<script>alert('Invalid Credential Details');location.href='/'</script>")

    print(request.session['uid'])
    if 'uid' in request.session:
        return render(request,'home.html')



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
    return render(request, 'post.html')

@csrf_exempt
def contact(request):
    return render(request, 'contact.html')

@csrf_exempt
def about(request):
    return render(request, 'about.html')



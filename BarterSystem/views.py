from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext
import json
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.cache import cache_page
from BarterSystem.models import *


# Create your views here.
def index(request):
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
def home(request):
    print(request.POST)
    if request.POST.get('email'):
        try:
            print("Password matched!!")
            user = User.objects.get(email=request.POST.get('email'))
            password = User.objects.get(password=request.POST.get('password'))
            return render(request, 'home.html')
        except:
            print ("Password not matching")
            return render(request, 'index.html')
    else:
        print("Incorrect")
        return render(request, 'index.html')

@csrf_exempt
def profile(request):
    return render(request, 'profile.html')

@csrf_exempt
def post(request):
    return render(request, 'post.html')

@csrf_exempt
def contact(request):
    return render(request, 'contact.html')

@csrf_exempt
def about(request):
    return render(request, 'about.html')



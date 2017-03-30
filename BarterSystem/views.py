from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext
import json
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.cache import cache_page

# Create your views here.
def index(request):
    return render(request,'index.html')

@csrf_exempt
def signin(request):
    return render(request,'signin.html')

@csrf_exempt
def signup(request):
    return render(request,'signup.html')

def home(request):
    return render(request,'homepage.html')

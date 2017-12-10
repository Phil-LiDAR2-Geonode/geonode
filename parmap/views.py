from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def other_rs(request):
    return HttpResponse("Hello, world. You're at the polls index.")
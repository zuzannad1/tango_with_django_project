from django.shortcuts import render

from django.http import HttpResponse

#The welcome page with link to about page 
def index(request):
    return HttpResponse("Rango says hey there partner! <br/> <a href='/rango/about/'>About</a>")

#The about page with link to welcome page
def about(request):
    return HttpResponse("Rango says here is about the page. <br/> <a href='/rango/welcome'>Index</a>")

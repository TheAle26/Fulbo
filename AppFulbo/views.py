from django.shortcuts import render, get_object_or_404, redirect
# from AppFulbo.models import
from django.http import HttpResponse, HttpResponseBadRequest
import datetime
# import AppFulbo.forms 
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def inicio(request):
    return render(request,"AppFulbo/inicio.html") #como tercer argumento le tengo que pasar en forma de diccionario la info
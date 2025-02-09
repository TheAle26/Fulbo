from django.http import HttpResponse
from django.template import loader, Template, Context

def saludo(request):
 return HttpResponse('Hola Django - Coder')
from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'app/index.html')

def forum(request):
    return render(request, 'app/forum.html')

def yarisma(request):
    return render(request, 'app/yarisma.html')

def hakkimizda(request):
    return render(request, 'app/hakkimizda.html')

def iletisim(request):
    return render(request, 'app/iletisim.html')

def login(request):
    return render(request, 'app/login.html')

def register(request):
    return render(request, 'app/register.html')

def privacy_policy(request):
    return render(request, 'app/privacy_policy.html')

def terms(request):
    return render(request, 'app/terms.html')

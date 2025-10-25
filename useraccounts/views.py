from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth import get_user_model

User = get_user_model()

def register_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            return render(request, 'useraccounts/register.html', {'error': 'Passwords do not match'})
        
        try:
            user = User.objects.create_user(email=email, username=username, password=password)
            user.save()
            return render(request, 'useraccounts/login.html', {'message': 'Registration successful. Please log in.'})
        except Exception as e:
            return render(request, 'useraccounts/register.html', {'error': str(e)})
    
    return render(request, 'useraccounts/register.html')

def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, 'useraccounts/login.html', {'error': 'Username not found.'})
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'useraccounts/login.html', {'error': 'Invalid credentials'})
    return render(request, 'useraccounts/login.html')

def logout_user(request):
    logout(request)
    return redirect('login')
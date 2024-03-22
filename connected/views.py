from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime
from connected.models import *
from connected.forms import *
from .models import ScheduleEntry

def add_event(request, tab_id):
    if request.method == 'POST':
        ScheduleEntry.objects.create(
            user=request.user,
            day=request.POST['day'],
            start_time=request.POST['start_time'],
            end_time=request.POST['end_time'],
            title=request.POST['title'],
            location=request.POST['location'],
            tab_id=tab_id
        )
        return redirect('tab_detail', tab_id=tab_id)

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    event_list = Event.objects.order_by('-views')[:5]
    context_dict = {}
    context_dict['categories'] = category_list
    context_dict['Events'] = event_list
    visitor_cookie_handler(request)
    response = render(request, 'connected/index.html', context=context_dict)
    return response

def home_view(request):
    return render(request, 'connected/home.html')

def about(request):
    context_dict = {}
    visitor_cookie_handler(request)
    context_dict['visits'] = int(request.COOKIES.get('visits', '1'))
    response = render(request, 'connected/about.html', context=context_dict)
    return response

def show_category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        events = Event.objects.filter(category=category)
        context_dict['events'] = events
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['events'] = None
    return render(request, 'connected/category.html', context=context_dict)


def hub_view(request):
    if request.user.is_authenticated:
        tabs = Tab.objects.filter(user=request.user)
        return render(request, 'connected/hub.html', {'tabs': tabs})
    else:
        return redirect('connected:login')

def add_tab(request):
    if request.method == 'POST' and request.user.is_authenticated:
        tab_name = request.POST.get('tab_name')
        Tab.objects.create(name=tab_name, user=request.user) 
        return redirect('connected:hub')
    else:
        return redirect('connected:login')

@login_required
def add_category(request):
    form = CategoryForm()
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        if form.is_valid():
            form.save(commit=True)
            return redirect('/connected/')
        else:
            print(form.errors)
    
    return render(request, 'connected/add_category.html', {'form': form})

@login_required
def add_event(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except:
        category = None
        
    if category is None:
        return redirect('/connected/')
        
    form = EventForm()
    
    if request.method == 'POST':
        form = EventForm(request.POST)
        
        if form.is_valid():
            if category:
                event = form.save(commit=False)
                event.category = category
                event.signups = 0
                event.save()
                
                return redirect(reverse('connected:show_category',
                                        kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)
                
    context_dict = {'form': form, 'category': category}
    return render(request, 'connected/add_page.html', context=context_dict)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('connected:hub')
    else:
        form = UserCreationForm()
    return render(request, 'connected/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('connected:index'))
            else:
                return HttpResponse("Your connected account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'connected/login.html')
    
@login_required
def restricted(request):
    return render(request, 'connected/restricted.html')

@login_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('inbox')
    else:
        form = MessageForm()
    return render(request, 'send_message.html', {'form': form})

@login_required
def inbox(request):
    received_messages = Message.objects.filter(receiver=request.user)
    return render(request, 'inbox.html', {'messages': received_messages})

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('connected:home'))

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits

class CustomLoginView(LoginView):
    template_name = 'connected/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('connected:home')

@login_required
def profile_view(request):
    return render(request, 'connected/profile.html', {'user': request.user})

def tab_detail_view(request, tab_id):
    tab = get_object_or_404(Tab, id=tab_id)
    return render(request, 'connected/tab_detail.html', {'tab': tab})

@login_required
def rename_tab(request, tab_id):
    tab = get_object_or_404(Tab, id=tab_id, user=request.user)
    if request.method == 'POST':
        tab.name = request.POST.get('new_name')
        tab.save()
        return HttpResponseRedirect(reverse('connected:hub'))
    return render(request, 'connected/rename_tab.html', {'tab': tab})

@login_required
def delete_tab(request, tab_id):
    tab = get_object_or_404(Tab, id=tab_id, user=request.user)
    if request.method == 'POST':
        tab.delete()
        return HttpResponseRedirect(reverse('connected:hub'))
    return render(request, 'connected/delete_tab_confirmation.html', {'tab': tab})

@login_required
def friends_list(request):
    add_friend_form = AddFriendForm()
    incoming_requests = FriendRequest.objects.filter(to_user=request.user)
    context = {
        'add_friend_form': add_friend_form,
        'incoming_requests': incoming_requests,
    }
    return render(request, 'connected/friends_list.html', context)

def send_message(request, receiver_id):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver_id = receiver_id
            message.save()
            return HttpResponseRedirect(reverse('connected:friends_list'))
    else:
        form = MessageForm()
    return render(request, 'connected/send_message.html', {'form': form})

@login_required
def add_friend(request):
    if request.method == 'POST':
        form = AddFriendForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user_to_add = User.objects.get(username=username)
                if user_to_add != request.user and not FriendRequest.objects.filter(from_user=request.user, to_user=user_to_add).exists():
                    FriendRequest.objects.create(from_user=request.user, to_user=user_to_add)
            except User.DoesNotExist:
                pass 
    return redirect('connected:friends_list')

@login_required
def handle_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    from_user_profile = friend_request.from_user.profile
    to_user_profile = friend_request.to_user.profile

    from_user_profile.friends.add(to_user_profile)
    to_user_profile.friends.add(from_user_profile)

    friend_request.delete()
    return redirect('some_redirect_target')


@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if request.user != to_user:
        FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
        messages.success(request, 'Friend request sent successfully.')
    else:
        messages.error(request, "You can't send a friend request to yourself.")
    return redirect('wherever_you_want_to_redirect')

from django.shortcuts import get_object_or_404, redirect
from .models import FriendRequest, User
from django.contrib.auth.decorators import login_required

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    friend_request.from_user.userprofile.friends.add(friend_request.to_user.userprofile)
    friend_request.to_user.userprofile.friends.add(friend_request.from_user.userprofile)
    friend_request.delete()
    return redirect('your_redirect_url')

def tab_detail(request, tab_id):
    schedule = {
        'monday': 'Your content for Monday',
        'tuesday': 'Your content for Tuesday',
        'wednesday': 'Your content for wednesday',
        'thursday': 'Your content for Thursday',
        'monday': 'Your content for Monday',
        'tuesday': 'Your content for Tuesday',
        'tuesday': 'Your content for Tuesday',
    }
    
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    context = {
        'tab': tab,
        'days_of_week': days_of_week,
        'schedule': schedule,
    }
    return render(request, 'tab_detail.html', context)


def weekly_schedule(request):
    if request.method == 'POST':
        form = ScheduleEntryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('weekly_schedule')
    else:
        form = ScheduleEntryForm()
    
    schedule_entries = ScheduleEntry.objects.filter(user=request.user)
    return render(request, 'weekly_schedule.html', {
        'form': form,
        'schedule_entries': schedule_entries,
    })
    
@login_required
def add_event(request, tab_id):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.tab = Tab.objects.get(pk=tab_id)
            event.save()
            return redirect('tab_detail', tab_id=tab_id)
    else:
        form = EventForm()
    return render(request, 'tab_detail.html', {'form': form})

@login_required
def save_schedule(request, tab_id):
    tab = get_object_or_404(Tab, pk=tab_id, user=request.user)
    if request.method == 'POST':
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            day_text = request.POST.get(day.lower())
    return redirect('tab_detail', tab_id=tab.id)
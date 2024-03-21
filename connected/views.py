from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime
from connected.models import Category, Event
from connected.forms import CategoryForm, EventForm, UserForm, UserProfileForm
from .models import Tab

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

# views.py in your Django app

def hub_view(request):
    if request.user.is_authenticated:
        tabs = Tab.objects.filter(user=request.user)  # Fetch tabs associated with the user
        return render(request, 'connected/hub.html', {'tabs': tabs})
    else:
        return redirect('connected:login')  # Redirect to login page if not authenticated


def add_tab(request):
    if request.method == 'POST' and request.user.is_authenticated:
        tab_name = request.POST.get('tab_name')
        Tab.objects.create(name=tab_name, user=request.user)  # Create a new tab for the user
        return redirect('connected:hub')  # Redirect back to the hub
    else:
        return redirect('connected:login')  # Redirect to login page if not authenticated or not POST request

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
            # Log the user in after registering
            login(request, user)
            return redirect('connected:hub')  # Redirect to the hub or another appropriate page
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
    
    # Import at the top
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

# Define your login view class
class CustomLoginView(LoginView):
    template_name = 'connected/login.html'
    redirect_authenticated_user = True  # Redirect users who are already logged in
    next_page = reverse_lazy('connected:home')  # Redirect to home after login

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def profile_view(request):
    return render(request, 'connected/profile.html', {'user': request.user})

from django.shortcuts import get_object_or_404, render
from .models import Tab

def tab_detail_view(request, tab_id):
    tab = get_object_or_404(Tab, id=tab_id)
    return render(request, 'connected/tab_detail.html', {'tab': tab})

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .models import Tab
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

@login_required
def rename_tab(request, tab_id):
    tab = get_object_or_404(Tab, id=tab_id, user=request.user)  # Assuming there's a user field
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

from django.shortcuts import render
from .models import Friend, Message

from django.shortcuts import render
from .forms import AddFriendForm

from django.shortcuts import render
from .forms import AddFriendForm

def friends_list(request):
    # Assuming you're passing friend requests and the add friend form
    add_friend_form = AddFriendForm()
    return render(request, 'connected/friends_list.html', {'add_friend_form': add_friend_form})



from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['message']

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

from django.shortcuts import render, redirect, get_object_or_404
from .models import FriendRequest
from .forms import AddFriendForm, FriendRequestResponseForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

@login_required
def add_friend(request):
    if request.method == 'POST':
        form = AddFriendForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user_to_add = User.objects.get(username=username)
                # Prevent sending a request to oneself and duplicate requests
                if user_to_add != request.user and not FriendRequest.objects.filter(from_user=request.user, to_user=user_to_add).exists():
                    FriendRequest.objects.create(from_user=request.user, to_user=user_to_add)
            except User.DoesNotExist:
                pass  # Handle error or add a message indicating the user doesn't exist
    return redirect('connected:friends_list')

@login_required
def handle_friend_request(request):
    if request.method == 'POST':
        action = request.POST.get('action', None)
        request_id = request.POST.get('request_id', None)
        friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
        
        if action == 'accept':
            friend_request.from_user.friends.add(request.user)  # Assuming you have a many-to-many relationship set up
            friend_request.to_user.friends.add(friend_request.from_user)
            friend_request.delete()
            messages.success(request, "Friend request accepted.")
        elif action == 'decline':
            friend_request.delete()
            messages.info(request, "Friend request declined.")
            
    return redirect('connected:friends_list')


from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import FriendRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if request.user != to_user:
        FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
        messages.success(request, 'Friend request sent successfully.')
    else:
        messages.error(request, "You can't send a friend request to yourself.")
    return redirect('wherever_you_want_to_redirect')


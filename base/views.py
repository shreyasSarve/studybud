from cmath import log
from email import message
from multiprocessing import context
from pydoc_data.topics import topics
import django
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Message, Room, Topic
from .forms import RoomForm, UserForm
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
# rooms = [
#     {'id': 1, 'name': "Let's Learn python"},
#     {'id': 2, 'name': 'Design with me'},
#     {'id': 3, 'name': "Frontend developers"},
# ]
# Create your views here.


def loginPage(request):
    print("inside login.....")
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            print('Username or password is invalid')
            messages.error(request, "Username or password is invalid")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            print('invalid creds')
            messages.error(request, "Invalid Credentials")

    context = {"page": page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    page = 'register'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        try:
            form = UserCreationForm(request.POST)
            print("form is created ......")
            if form.is_valid():
                print("valid form")
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Error Occured While Registration")
        except:
            messages.error(request, "Error Occured")
    form = UserCreationForm()
    context = {'page': page, 'form': form}
    return render(request, 'base/login_register.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q) |
                                Q(name__icontains=q) |
                                Q(disciption__icontains=q) |
                                Q(host__username__icontains=q)
                                )
    topics = Topic.objects.all()[:5]
    room_messages = Message.objects.all().filter(Q(room__topic__name__icontains=q))
    room_count = rooms.count()
    context = {'rooms': rooms, 'topics': topics,
               'rooms_count': room_count, 'messages': room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room': room, 'messages': room_messages,
               'participants': participants}
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm
    topics = Topic.objects.all()
    context = {'form': form, 'topics': topics}
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            disciption=request.POST.get('disciption')
        )
        return redirect('home')
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    topics = Topic.objects.all()
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("You are not allowed to delete this.....")
    form = RoomForm(instance=room)
    context = {'form': form, 'topics': topics, 'room': room}
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.disciption = request.POST.get('disciption')
        print(request.POST.get('name'))
        room.save()
        return redirect('home')
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("You are not allowed to delete this.....")
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {"obj": room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse("You are not allowed to delete this.....")
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {"obj": message})
# @login_required(login_url='login')


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
               'messages': room_messages, "topics": topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def updateProfile(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('userprofile', pk=user.id)
    context = {'form': form}
    return render(request, 'base/update-user.html', context)


def topicsPage(request):
    rooms_count = Room.objects.all().count
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics': topics, 'rooms_count': rooms_count}
    return render(request, 'base/topics.html', context)

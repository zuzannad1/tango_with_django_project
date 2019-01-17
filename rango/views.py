from django.shortcuts import render
from rango.models import Category, Page
from django.http import HttpResponse, HttpResponseRedirect
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse
from datetime import datetime



def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    response = render(request, 'rango/index.html', context=context_dict)
    return response


def about(request):
    print(request.method)
    print(request.user)
    count = request.session.get('visits',0)
    context_dict = {}
    context_dict['visit_count']=count
    return render(request, 'rango/about.html', context = context_dict)

def show_category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)
            
    context_dict = {'form':form, 'category': category, 'category_name_slug': category_name_slug}
    return render(request, 'rango/add_page.html', context_dict)

def register(request):
    registered = False
    if(request.method == 'POST'):
        userForm = UserForm(data=request.POST)
        profileForm = UserProfileForm(data=request.POST)

        if((userForm.is_valid()) and (profileForm.is_valid())):
            user = userForm.save()
            user.set_password(user.password)
            user.save()

            profile = profileForm.save(commit=False)
            profile.user = user

            if('profileImage' in request.FILES):
                profile.profileImage = request.FILES['profileImage']

            profile.save()

            registered = True

        else:
            print(userForm.errors, profileForm.errors)

    else:
        userForm = UserForm()
        profileForm = UserProfileForm()

    return render(request, 'rango/register.html',
                  {'userForm':userForm, 'profileForm':profileForm, 'registered':registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html',{})

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request,
                                               'last_visit',
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
'%Y-%m-%d %H:%M:%S')
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
      request.session['last_visit']=last_visit_cookie

    request.session['visits'] = visits

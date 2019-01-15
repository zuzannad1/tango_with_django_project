from django.shortcuts import render
from rango.models import Category, Page
from django.http import HttpResponse, HttpResponseRedirect
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm
from django.urls import reverse
from django.contrib.auth import authenticate, login


#The welcome page with link to about page 
def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}
    return render(request, 'rango/index.html', context_dict)

    
# The about page with link to welcome page
def about(request):
# prints out whether the method is a GET or a POST
    print(request.method)
# prints out the user name, if no one is logged in it prints `AnonymousUser`
    print(request.user)
    return render(request, 'rango/about.html', {})

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
        userForm = forms.UserForm(data=request.POST)
        profileForm = forms.UserProfileInfoForm(data=request.POST)

        if((userForm.is_valid()) and (profileForm.id_valid())):
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

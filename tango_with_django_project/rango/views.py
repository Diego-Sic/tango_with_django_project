from django.shortcuts import render, redirect
from rango.models import Category
from rango.models import Category, Page
from rango.forms import PageForm
from django.shortcuts import redirect
from .forms import CategoryForm
from rango.forms import UserForm, UserProfileForm
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout


def index(request):
    # Query the database for a list of categories ordered by likes (top 5).
    category_list = Category.objects.order_by('-likes')[:5]

    # Query the database for a list of pages ordered by views (top 5).
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {
        'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!',
        'categories': category_list,
        'pages': page_list  # Pass pages to the template
    }

    return render(request, 'rango/index.html', context=context_dict)


def about(request):
    return render(request, 'rango/about.html')

def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass
    # to the template rendering engine.
    context_dict = {}
    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # The .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
        # Retrieve all of the associated pages.
        # The filter() will return a list of page objects or an empty list.
        pages = Page.objects.filter(category=category)
        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from
        # the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything -
        # the template will display the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None
        # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect('/rango/')
        else:
            print(form.errors)  # Print errors to the console for debugging

    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    # You cannot add a page to a Category that does not exist...
    if category is None:
        return redirect('/rango/')
    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return redirect(reverse('rango:show_category', kwargs={'category_name_slug':category_name_slug}))
    else:
        print(form.errors)
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def register(request):    
    registered = False  # Indicates if registration was successful

    if request.method == 'POST':
        # Retrieve form data from the POST request
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            # Save user form data to the database
            user = user_form.save(commit=False)
            user.set_password(user.password)  # Hash password
            user.save()

            # Create and save user profile
            profile = profile_form.save(commit=False)
            profile.user = user

            # If the user uploaded a picture, save it
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True  # Registration was successful
        else:
            # Print form errors for debugging
            print(user_form.errors, profile_form.errors)
    else:
        # Render empty forms for user registration
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the registration page with form data
    return render(
        request,
        'rango/register.html',
        {
            'user_form': user_form,
            'profile_form': profile_form,
            'registered': registered
        }
    )


def user_login(request):
    """Handles user authentication and login process."""

    if request.method == 'POST':
        # Get username and password from the form
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                # Log the user in and redirect to homepage
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Invalid login attempt
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")

    # If GET request, show login page
    return render(request, 'rango/login.html')


@login_required
def restricted(request):
    """Restricted page only visible to logged-in users."""
    return render(request, 'rango/restricted.html')


@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect(reverse('rango:index'))
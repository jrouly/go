from go.models import URL
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

# Homepage view.
@login_required
def index(request):
    return render(request, 'index.html', {

    },
    )

# My-Links page.
@login_required
def my_links(request):
    links = URL.objects.filter( owner = request.user )

    return render(request, 'my_links.html', {
        'links' : links,
    },
    )

# Delete link page.
@login_required
def delete(request, short):
    url = URL.objects.get( short = short )
    if url.owner == request.user:
        url.delete()
    return redirect('my_links')

# About page, static.
def about(request):
    return render(request, 'about.html', {

    },
    )

# Signup page.
def signup(request):
    return render(request, 'signup.html', {

    },
    )

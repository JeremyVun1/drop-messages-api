# Views for web based end points
# Jeremy Vun 2726092

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

# 404
def no_resource(request):
    return render(request, '404.html')


# web portal for testing socket connections and messages
def web_portal(request):
    return render(request, 'portal.html')


# register with POST
def web_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]

            return redirect('web_portal')
    else:
        form = UserCreationForm()

    template = "registration/registration.html"
    context = {
        "form": form
    }
    return render(request, template, context)

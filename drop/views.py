# Views for web based end points
# Jeremy Vun 2726092

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .serializers import UserSerializer
from rest_framework.generics import CreateAPIView
from rest_framework import permissions

# 404
from rest_framework.decorators import api_view


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


# generic model view for creating models via REST API
class RegisterUserView(CreateAPIView):
	serializer_class = UserSerializer
	permission_classes = [permissions.AllowAny]
	model = User

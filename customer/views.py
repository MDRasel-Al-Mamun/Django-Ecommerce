from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from django.contrib.auth import login


@login_required(login_url='signin')
def profileView(request):
    current_user = request.user
    profile = UserProfile.objects.get(user_id=current_user.id)
    context = {
        'profile': profile,
    }
    return render(request, 'customer/profile.html', context)


@login_required(login_url='signin')
def profileUpdate(request):
    profile = UserProfile.objects.get(user__id=request.user.id)
    values = UserProfile.objects.get(user__id=request.user.id)
    context = {
        'profile': profile,
        'values': values
    }
    if request.method == 'POST':
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        address = request.POST["address"]
        city = request.POST["city"]
        state = request.POST["state"]
        country = request.POST["country"]
        zipcode = request.POST["zipcode"]

        user = User.objects.get(id=request.user.id)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        values.address = address
        values.phone = phone
        values.city = city
        values.state = state
        values.country = country
        values.zipcode = zipcode

        values.save()
        messages.success(request, 'Profile Update Successfully')

        if "image" in request.FILES:
            image = request.FILES["image"]
            values.image = image
            values.save()

        return redirect('profile')
    return render(request, 'customer/update.html', context)


@login_required(login_url='signin')
def changePassword(request):
    profile = UserProfile.objects.get(user__id=request.user.id)
    context = {
        'profile': profile,
    }
    if request.method == 'GET':
        return render(request, 'customer/change_password.html', context)

    if request.method == 'POST':
        old_password = request.POST['old_password']
        password = request.POST['password']

        user = User.objects.get(id=request.user.id)
        check = user.check_password(old_password)
        if check == True:
            user.set_password(password)
            user.save()
            messages.success(request, 'Password Change Successfully')
            user = User.objects.get(username=user.username)
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Old password is not metch')
            return render(request, 'customer/change_password.html', context)

        return render(request, 'customer/change_password.html', context)

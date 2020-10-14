from django.shortcuts import render


def homeView(request):
    context = {}
    return render(request, 'home/index.html', context)

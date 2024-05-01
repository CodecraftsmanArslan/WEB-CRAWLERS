from django.shortcuts import render,redirect
from .models import YourModelName
from django.shortcuts import get_object_or_404


def add_post(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        header_image = request.FILES.get('image')  # Use request.FILES for file uploads
        new_post = YourModelName(title=title, description=description, header_image=header_image)
        new_post.save()

    return render(request, 'add_post.html')


def index(request):
    all_data = YourModelName.objects.all()
    data_list = [{'id': data.id, 'title': data.title, 'description': data.description, 'image_url': data.header_image.url} for data in all_data]
    return render(request, 'index.html', {'data': data_list})


def edit(request, pk):
    edit_single = get_object_or_404(YourModelName, id=pk)
    if request.method == 'POST':
        edit_single.title = request.POST.get('title')
        edit_single.description = request.POST.get('description')
        # edit_single.image_url= request.FILES.get('image')
        edit_single.save()
        return redirect('index')
    return render(request, 'edit.html', {'edit_it': [edit_single]})  


def delete(request, pk):
    element = YourModelName.objects.get(id=pk)  
    element.delete()
    return redirect('/')









from django.shortcuts import render,redirect
from .models import YourModelName

def index(request):
    # Fetching all instances of YourModelName
    all_data = YourModelName.objects.all()
    data_list = [{'id': data.id, 'title': data.title, 'description': data.description} for data in all_data]
    return render(request, 'index.html', {'data': data_list})




# def edit():
    
    
    
    
def delete(request, pk):
    element = YourModelName.objects.get(id=pk)  
    element.delete()
    return redirect('/')











from django.shortcuts import render

def word_count(request):
    data = None
    if request.method == "POST":
        word = request.POST.get('texttocount', '')
        data = len(word.split())
        
    return render(request, 'index.html', {'data': data})




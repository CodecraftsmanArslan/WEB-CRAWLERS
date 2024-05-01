from django.shortcuts import render,HttpResponse
from translate import Translator

def translated_text(request):
    data = None
    if request.method == "POST":
        text = request.POST.get('textInput')
        language = request.POST.get('languageSelect')
        translator = Translator(to_lang=language)
        translated_text = translator.translate(text)
        return HttpResponse(translated_text) 
    return render(request, 'index.html')

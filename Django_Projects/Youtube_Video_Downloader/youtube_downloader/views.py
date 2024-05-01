from django.shortcuts import render
from .models import Video
from pytube import *
from django.contrib import messages



def video_downloader(request):
    if request.method == 'POST':
        url = request.POST.get('link')  # Correct usage of request.POST
        video = Video.objects.create(link=url)
        video.save()
        yt = YouTube(url)
        
        # Get the lowest resolution stream
        stream = yt.streams.get_lowest_resolution()
        
        # Download the video
        stream.download()

        messages.success(request, 'Video downloaded successfully!')


    return render(request,'index.html')




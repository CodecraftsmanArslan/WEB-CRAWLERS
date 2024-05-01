from django.shortcuts import render
from .models import Event

def timer(request):
    event = Event.objects.first()  # Assuming you have an Event object stored in the database
    initial_event_time = event.event  # Get the initial event time from the database

    # Calculate initial hours, minutes, and seconds
    hours = initial_event_time // 3600
    minutes = (initial_event_time // 60) % 60
    seconds = initial_event_time % 60

    return render(request, 'index.html', {'hours': hours, 'minutes': minutes, 'seconds': seconds})

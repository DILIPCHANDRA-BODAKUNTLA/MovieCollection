from django.contrib import admin
from .models import Collection, Movie, MovieCollection, RequestData

admin.site.register(Collection)
admin.site.register(Movie)
admin.site.register(MovieCollection)
admin.site.register(RequestData)

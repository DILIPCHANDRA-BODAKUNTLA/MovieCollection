import uuid

from django.db import models
from django.contrib.auth.models import User


class Collection(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    collection_uuid = models.UUIDField(unique=True, auto_created=True,default=uuid.uuid4,)
    movies = models.ManyToManyField('Movie', through='MovieCollection', related_name='collections')
    is_success = models.BooleanField(default=True)

    class Meta:
        db_table = 'collection'
        unique_together = ('title', 'user')


class Movie(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    genres = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.UUIDField(unique=True,default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'movie'


class MovieCollection(models.Model):
    """
    Through table representing the many-to-many relationship between collections and movies,
    with additional metadata about the relationship.
    """
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "movie_collection"


def get_request_id():
    return str(uuid.uuid4())[:10]


class RequestData(models.Model):
    request_id = models.CharField(max_length=255, unique=True, default=get_request_id)
    user = models.IntegerField(null=True, default=0, db_index=True)
    method = models.CharField(max_length=50)
    path = models.CharField(max_length=255)
    request_time = models.DateTimeField(db_index=True)
    body = models.TextField(null=True, blank=True)
    meta_data = models.JSONField(null=True, blank=True)
    headers = models.TextField(null=True)
    response_status = models.CharField(null=True, max_length=255)
    response_data = models.TextField(null=True, blank=True)
    query_params = models.JSONField(null=True)
    ip_address = models.CharField(max_length=42)
    cookies = models.JSONField(null=True)
    request_date = models.DateField(null=True, blank=True, db_index=True)
    execution_time = models.DurationField(null=True)
    node_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    client = models.CharField(null=True, max_length=100)
    query_count = models.JSONField(null=True)
    request_type = models.CharField(max_length=255,null=-True,blank=True)

    class Meta:
        db_table = 'requests_tracking'

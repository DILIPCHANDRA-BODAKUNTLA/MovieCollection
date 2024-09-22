from django.contrib.auth.models import User, Permission, Group
from rest_framework import serializers
from .models import Collection, Movie, RequestData


class MovieSerializer(serializers.ModelSerializer):
    uuid = serializers.CharField(read_only=True)

    class Meta:
        model = Movie
        fields = "__all__"


class CollectionSerializer(serializers.ModelSerializer):
    movies = MovieSerializer(many=True, read_only=True)
    collection_uuid = serializers.CharField(read_only=True)

    class Meta:
        model = Collection
        fields = "__all__"

    def create_movies_return_ids(self, movies):
        movies_list, movies_title_from_input = [], []
        for movie in movies:
            if movie.get("title"):
                movies_title_from_input.append(movie.get("title"))
            movies_list.append(Movie(**movie))
        if movies_list:
            Movie.objects.bulk_create(movies_list, ignore_conflicts=True)
        return list(Movie.objects.filter(title__in=movies_title_from_input).values_list("id", flat=True))

    def create(self, validated_data):
        movies = self.initial_data.pop("movies", [])
        collection = Collection.objects.create(**validated_data)
        movies_id = self.create_movies_return_ids(movies)
        collection.movies.set(movies_id)
        return collection

    def update(self, instance, validated_data):
        movies = self.initial_data.pop("movies", [])
        if movies:
            instance.movies.clear()
            movies_id = self.create_movies_return_ids(movies)
            instance.movies.set(movies_id)
        return super(CollectionSerializer, self).update(instance, validated_data)

class RequestDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = RequestData
        fields = "__all__"



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id","username","email","password","first_name","last_name","is_superuser","is_staff","is_active"]
class CollectionListSerializer(serializers.ModelSerializer):
    user = UserListSerializer()
    movies = MovieSerializer(many=True,read_only=True)

    class Meta:
        model = Collection
        fields = "__all__"





import requests
from django.db import transaction
from django.db.models import Prefetch
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, \
    DestroyModelMixin
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

from .constants import Constant
from .models import Collection, Movie, RequestData, MovieCollection
from .serializers import CollectionSerializer, MovieSerializer, RequestDataSerializer, UserSerializer, \
    CollectionListSerializer, UserListSerializer
from user_collections.settings import env
from .utilities import get_retry_session
from .pagination import CustomPageNumberPagination


class RegisterAPI(GenericViewSet, CreateModelMixin):
    """
    user can register,authentication is not required for this class
    """
    permission_classes = []

    def create(self, request, *args, **kwargs):
        ser = UserSerializer(data=request.data)
        if ser.is_valid(raise_exception=True):
            user = ser.save()
            refresh = RefreshToken.for_user(user)
            return Response({'refresh_token': str(refresh), 'access_token': str(refresh.access_token)}, status=200)
        return Response(ser.errors, status=500)

    @action(methods=['POST'], detail=False, url_path="generate_token")
    def generate_accesstoken(self,request, *args, **kwargs):
        user = User.objects.filter(**request.data).first()
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({'refresh_token': str(refresh), 'access_token': str(refresh.access_token)}, status=200)
        else:
            return Response({"message":"User does not exists with given credentials"})



class UserAPI(GenericViewSet, CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, ListModelMixin):
    """
    only superuser can view all users details and can edit data
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        else:
            return User.objects.filter(id=self.request.user.id)

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return UserSerializer
        else:
            return UserListSerializer



class MovieAPI(GenericViewSet, ListModelMixin):
    """
    movies list is called from external api.This list is not stored in database
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MovieSerializer

    def get_queryset(self):
        return Movie.objects.all()

    def list(self, request, *args, **kwargs):
        retry_session = get_retry_session()
        try:
            response = retry_session.get(env(Constant.MOVIE_API_URL),params=request.query_params.copy(),verify=False)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=500)
        return Response(response.json(), status=response.status_code)

class MoviesFromDbAPI(GenericViewSet, ListModelMixin,UpdateModelMixin,RetrieveModelMixin,CreateModelMixin):
    """
    movies list is called from external api.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MovieSerializer

    def get_queryset(self):
        return Movie.objects.all()


class CollectionAPI(GenericViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin,
                    DestroyModelMixin):
    """
    CRUD APIs for Collection,here movies are first created in database and then assigned to user collection and movie title is assumed to be unique,collection title is unique for each user.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    pagination_class = CustomPageNumberPagination

    ordering_fields = ['title']
    search_fields = ['title']
    ordering = ['-id']

    def get_queryset(self):
        qs = Collection.objects.all().prefetch_related(Prefetch("user",queryset=User.objects.all()),'movies')
        if self.request.user.is_superuser:
            return qs
        else:
            return qs.filter(user_id=self.request.user.id)


    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update','delete']:
            return CollectionSerializer
        else:
            return CollectionListSerializer

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            input_data = request.data
            if "user" not in input_data:
                input_data["user"] = request.user.id
            ser = CollectionSerializer(data=input_data)
            if ser.is_valid(raise_exception=True):
                instance = ser.save()
                output_data = CollectionListSerializer(instance).data
                return Response(output_data, status=201)
            return Response(ser.errors, status=400)

    def update(self,request,*args,**kwargs):
        with transaction.atomic():
            input_data = request.data
            if "user" not in input_data:
                input_data["user"] = self.get_object().user.id
            ser = CollectionSerializer(instance =self.get_object(),data=input_data)
            if ser.is_valid(raise_exception=True):
                instance = ser.save()
                output_data = CollectionListSerializer(instance).data
                return Response(output_data, status=200)
            return Response(ser.errors, status=400)

    def partial_update(self, request, *args, **kwargs):
        with transaction.atomic():
            input_data = request.data
            if "user" not in input_data:
                input_data["user"] = self.get_object().user.id
            ser = CollectionSerializer(instance =self.get_object(),data=input_data,partial=True)
            if ser.is_valid(raise_exception=True):
                instance = ser.save()
                output_data = CollectionListSerializer(instance).data
                return Response(output_data, status=200)
            return Response(ser.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.movies.clear()
        instance.delete()
        return Response({"collection deleted successfully"},status=200)



class RequestDataAPI(GenericViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin,
                     DestroyModelMixin):
    """
    CRUD APIs for RequestLog.It stored data of request logs and total time taken by api and number of sql queries executed in each request is also stored.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RequestDataSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    pagination_class = CustomPageNumberPagination

    ordering_fields = []
    search_fields = []

    def get_queryset(self):
        return RequestData.objects.all()

    def list(self, request, *args, **kwargs):
        no_of_requests = self.get_queryset().count()
        return Response({"requests": "{} requests are served by server till now".format(no_of_requests)})

    @action(methods=['POST'], detail=False, url_path="reset")
    def reset(self, request, *args, **kwargs):
        self.get_queryset().delete()
        return Response({"message": "request count reset successfully"}, status=200)

    @action(methods=['get'], detail=False, url_path="request-log")
    def get_request_log(self, request, *args, **kwargs):
        return Response(RequestDataSerializer(self.get_queryset(),many=True).data)


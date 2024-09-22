import copy

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase, APIClient
from movie_collection.models import Collection
import random
import string


def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def get_access_token(user_id):
    user = User.objects.filter(id=user_id).first()
    refresh = RefreshToken.for_user(user)
    return refresh.access_token


class UserCollectionTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        """
        creates the return accesstoken
        """
        cls.client = APIClient()
        cls.user_id = 1
        cls.access_token = get_access_token(user_id=cls.user_id)
        cls.headers = {'HTTP_AUTHORIZATION': f'Bearer {cls.access_token}'}
        cls.collections_path = "/collection/"

    def setUp(self):
        """
        sets authorization token to api client.
        """
        self.client = APIClient()
        self.client.defaults['HTTP_AUTHORIZATION'] = UserCollectionTest.headers.get('HTTP_AUTHORIZATION')

    def test_collection_list(self):
        resp = self.client.get(path=self.collections_path)
        self.assertEqual(resp.status_code, 200)

    def test_collection_retrieve(self):
        user_collection_obj = Collection.objects.filter().first()
        if user_collection_obj:
            resp = self.client.get(path=self.collections_path + "{}/".format(user_collection_obj.id))
            self.assertEqual(resp.status_code, 200)

    def test_collection_post_put_patch(self):
        data = {
            "user": self.user_id,
            "movies": [
                {
                    "uuid": "36508803-1366-4058-b619-1fc0c6ada063",
                    "title": "Fobos. Klub Strakha",
                    "description": "Rainy summer evening... Young people are arriving at the new trendy club named Phobos which is still under construction. Or re-construction - since it's a former bomb shelter which is reconstructed to become a club. At first, the party sees nothing wrong, but soon the bunker doors turn out to be locked, and the teenagers get trapped underground without light and communication. At first, all of them are joking and do not realize how dangerous their situation is. Then they get frightened. All of them will need to cope with their fears before the bunker will let them free.",
                    "genres": "Thriller,Horror"
                },
                {
                    "uuid": "ab272b37-c1ac-4cb2-bc3a-11f0d91516d6",
                    "title": "Le Meraviglie di Aladino",
                    "description": "Young Aladdin (Donald O'Connor) has a series of wild adventures after he discovers a magic lamp containing a genie (Vittorio De Sica).",
                    "genres": ""
                },
                {

                    "uuid": "36508803-1366-4058-b619-1fc0c6ada021",
                    "title": "bahubali",
                    "description": "Rainy summer evening... Young people are arriving at the new trendy club named Phobos which is still under construction. Or re-construction - since it's a former bomb shelter which is reconstructed to become a club. At first, the party sees nothing wrong, but soon the bunker doors turn out to be locked, and the teenagers get trapped underground without light and communication. At first, all of them are joking and do not realize how dangerous their situation is. Then they get frightened. All of them will need to cope with their fears before the bunker will let them free.",
                    "genres": "Thriller,Horror"
                }
            ],
            "title": "test user collection one" + generate_random_string(8),
            "description": "this collection contains 5 movies"
        }
        resp = self.client.post(path=self.collections_path, data=data, format="json")
        self.assertEqual(resp.status_code, 201)
        created_obj_from_db = None
        print("durrrr")
        if resp.status_code == 201:
            resp_data = resp.data
            print("eeww", resp_data)
            collection_id = resp_data.get("id")
            created_obj_from_db = Collection.objects.filter(id=collection_id).first()
            if created_obj_from_db:
                self.assertEqual(data.get("title"), created_obj_from_db.title)
                self.assertEqual(data.get("description"), created_obj_from_db.description)
                self.assertEqual(data.get("user"), created_obj_from_db.user.id)
                self.assertEqual(len(data.get("movies")), created_obj_from_db.movies.all().count())

        # test put method here
        if created_obj_from_db:
            put_data = {
                "id": created_obj_from_db.id,
                "user": self.user_id,
                "movies": [
                    {
                        "uuid": "36508803-1366-4058-b619-1fc0c6ada063",
                        "title": "Fobos. Klub Strakha",
                        "description": "Rainy summer evening... Young people are arriving at the new trendy club named Phobos which is still under construction. Or re-construction - since it's a former bomb shelter which is reconstructed to become a club. At first, the party sees nothing wrong, but soon the bunker doors turn out to be locked, and the teenagers get trapped underground without light and communication. At first, all of them are joking and do not realize how dangerous their situation is. Then they get frightened. All of them will need to cope with their fears before the bunker will let them free.",
                        "genres": "Thriller,Horror"
                    },
                    {
                        "uuid": "ab272b37-c1ac-4cb2-bc3a-11f0d91516d6",
                        "title": "Le Meraviglie di Aladino",
                        "description": "Young Aladdin (Donald O'Connor) has a series of wild adventures after he discovers a magic lamp containing a genie (Vittorio De Sica).",
                        "genres": ""
                    }
                ],
                "title": "test user collection one update"+generate_random_string(8),
                "description": "this collection contains 5 movies updated"
            }
            put_resp = self.client.put(path='{}{}/'.format(self.collections_path, created_obj_from_db.id), data=put_data,
                                       format="json")
            put_resp_data = put_resp.data
            print(put_resp_data)
            self.assertEqual(put_resp.status_code, 200)
            if put_resp.status_code==200:
                self.assertEqual(put_data.get("title"), put_resp_data.get("title"))
                self.assertEqual(put_data.get("description"), put_resp_data.get("description"))
                self.assertEqual(len(put_data.get("movies")), len(put_resp_data.get("movies")))

        # test patch here
        if created_obj_from_db:
            patch_data = {
                "id": created_obj_from_db.id,
                "description": "this collection contains 5 movies partial update"
            }
            patch_resp = self.client.patch(path='{}{}/'.format(self.collections_path, created_obj_from_db.id),
                                           data=patch_data,
                                           format="json")
            patch_resp_data = patch_resp.data
            self.assertEqual(patch_resp.status_code, 200)
            if patch_resp.status_code == 200:
                self.assertEqual(patch_data.get("description"), patch_resp_data.get("description"))

        # test delete here
        if created_obj_from_db:
            delete_id = created_obj_from_db.id
            delete_resp = self.client.delete(path='{}{}/'.format(self.collections_path, created_obj_from_db.id),
                                             data=put_data,
                                             format="json")
            self.assertEqual(delete_resp.status_code, 200)
            if delete_resp.status_code ==200:
                deleted_obj = Collection.objects.filter(id=delete_id).first()
                self.assertEqual(deleted_obj, None)

    @classmethod
    def tearDownClass(cls):
        """
        Executes only once for class after all the tests have run.
        """
        pass


class MovieTestClass(APITestCase):
    @classmethod
    def setUpClass(cls):
        """
        creates the return accesstoken
        """

        cls.client = APIClient()
        cls.user_id = 1
        cls.access_token = get_access_token(user_id=cls.user_id)
        cls.headers = {'HTTP_AUTHORIZATION': f'Bearer {cls.access_token}'}
        cls.movies_path = "/movies/"

    def setUp(self):
        """
        sets authorization token to api client.
        """
        self.client = APIClient()
        self.client.defaults['HTTP_AUTHORIZATION'] = MovieTestClass.headers.get('HTTP_AUTHORIZATION')

    def test_movie_list(self):
        resp = self.client.get(path=self.movies_path)
        self.assertEqual(resp.status_code, 200)

    @classmethod
    def tearDownClass(cls):
        """
        Executes only once for class after all the tests have run.
        """
        pass


class RequestLogTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        """
        creates the return accesstoken
        """

        cls.client = APIClient()
        cls.user_id = 1
        cls.access_token = get_access_token(user_id=cls.user_id)
        cls.headers = {'HTTP_AUTHORIZATION': f'Bearer {cls.access_token}'}
        cls.request_count_path = "/request-count/"

    def setUp(self):
        """
        sets authorization token to api client.
        """
        self.client = APIClient()
        self.client.defaults['HTTP_AUTHORIZATION'] = RequestLogTest.headers.get('HTTP_AUTHORIZATION')

    def test_request_count(self):
        resp = self.client.get(path=self.request_count_path)
        self.assertEqual(resp.status_code, 200)

    def test_request_count_reset(self):
        resp = self.client.post(path=self.request_count_path + "reset/")
        self.assertEqual(resp.status_code, 200)

    @classmethod
    def tearDownClass(cls):
        """
        Executes only once for class after all the tests have run.
        """
        pass


class UserTestClass(APITestCase):
    @classmethod
    def setUpClass(cls):
        """
        creates the return accesstoken
        """

        cls.client = APIClient()
        cls.user_id = 1
        cls.register_path = "/register/"

    def setUp(self):
        """
        sets authorization token to api client.
        """
        self.client = APIClient()

    def test_user_register(self):
        data = {"username": "testusertoday" + generate_random_string(8), "password": "1234"}
        resp = self.client.post(path=self.register_path,data=data, format="json")
        self.assertEqual(resp.status_code, 201)

    @classmethod
    def tearDownClass(cls):
        """
        Executes only once for class after all the tests have run.
        """
        pass

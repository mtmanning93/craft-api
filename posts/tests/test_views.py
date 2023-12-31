from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from rest_framework import status
from ..models import Post
from ..serializers import PostSerializer


class PostListViewTest(APITestCase):
    """
    Tests for the PostList view,
    including listing and creating.
    """
    def setUp(self):
        """
        Set up test object instances.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
            )

        self.post = Post.objects.create(
            owner=self.user,
            title='Test Post',
            content='This is a test post'
            )

        self.post_data = {
            'title': 'Test Post 2',
            'content': 'I love testing'}

        self.client = APIClient()
        self.response = self.client.get('/posts/')
        self.client.force_authenticate(user=self.user)

    def test_list_posts(self):
        """
        Test PostList view simple returns a successful response.
        Test created Post instance appear in the list.
        """
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.count(), 1)

    def test_create_post(self):
        """
        Tests that an authenticated user can create a post and add it to
        the post list.
        Checks for a successful status code and that the posts count
        has been incremented.
        """
        response = self.client.post('/posts/', self.post_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)


class PostDetailViewTest(APITestCase):
    """
    Testcase for the PostDetail view,
    including updating and deleting as an authenticated user.
    """
    def setUp(self):
        """
        Set up test data.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
            )
        self.post = Post.objects.create(
            owner=self.user,
            title='Test Post',
            content='This is a test post'
            )

        self.client = APIClient()
        self.response = self.client.get('/posts/')
        self.client.force_authenticate(user=self.user)

    def test_retrieve_post(self):
        """
        Checks the retrieval of a specific post instance is successful.
        """
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def test_update_post(self):
        """
        Checks that an authenticated user can update a post.
        First checks the original data, then the updated post data.
        """
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.content, 'This is a test post')

        update_data = {
            'title': 'Updated Post',
            'content': 'This post has been updated'
            }

        response = self.client.put(
            f'/posts/{self.post.pk}/', update_data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Post')

    def test_delete_post(self):
        """
        Tests to see if an authenticated user can also delete a post.
        """
        response = self.client.delete(f'/posts/{self.post.pk}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.filter(pk=self.post.pk).count(), 0)

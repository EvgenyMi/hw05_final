from http import HTTPStatus

from django.test import Client, TestCase
from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestAuthor')
        cls.user_not_author = User.objects.create_user(username='NotAuthor')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='post-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def setUp(self):
        self.client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user_not_author)

    def test_urls_with_guest_access(self):
        url_names = {
            '/',
            '/group/post-slug/',
            '/profile/TestAuthor/',
            f'/posts/{self.post.pk}/',
        }
        for address in url_names:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_with_authorised_access(self):
        url_names = {
            '/',
            '/group/post-slug/',
            '/profile/TestAuthor/',
            f'/posts/{self.post.pk}/',
            f'/posts/{self.post.pk}/edit/',
            '/create/',
        }
        for address in url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_redirect(self):
        url_names = {
            f'/posts/{self.post.pk}/edit/': (
                f'/auth/login/?next=/posts/{self.post.pk}/edit/'),
            '/create/': '/auth/login/?next=/create/',
        }
        for address, redirect_address in url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address, follow=True)
                self.assertRedirects(response, redirect_address)

    def test_urls_use_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': "posts/index.html",
            '/group/post-slug/': 'posts/group_list.html',
            '/profile/TestAuthor/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_page_not_found(self):
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='first',
        )
        cls.post = Post.objects.create(
            text='Тестовая запись',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        Post.objects.all().delete()
        posts_count = Post.objects.count()

        form_data = {
            'group': self.group.pk,
            'text': 'Тестовый текст через форму',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={"username": "TestAuthor"}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest('pk')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.pk, form_data['group'])

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post"""
        posts_count = Post.objects.count()

        form_data = {
            'group': self.group.pk,
            'text': 'Отредактированный тестовый текст через форму',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': str(self.post.pk)}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': str(self.post.pk)}))
        self.assertEqual(Post.objects.count(), posts_count)
        post = Post.objects.latest('pk')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.pk, form_data['group'])

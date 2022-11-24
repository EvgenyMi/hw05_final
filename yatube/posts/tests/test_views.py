import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post, User


class GroupPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestAuthor')
        cls.user_second = User.objects.create_user(username='TestSecondAuthor')
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Группа',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.group_second = Group.objects.create(
            title="Группа2",
            slug="test-slug2",
            description="Тестовое описание второй группы",
        )
        cls.post = []
        objs = [
            Post(
                author=cls.user,
                text="Тестовый текст",
                group=cls.group,
                image=cls.uploaded,
            )
            for i in range(12)
        ]
        cls.post = Post.objects.bulk_create(objs)
        cls.post_from_second_group = Post.objects.create(
            author=cls.user_second,
            text="Тестовый текст",
            group=cls.group_second,
            image=cls.uploaded,
        )

    def setUp(self):
        self.client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_second = Client()
        self.authorized_client_second.force_login(self.user)
        cache.clear()

    def test_page_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        page_name_template = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": "test-slug"}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": "TestAuthor"}
            ): "posts/profile.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }

        for reverse_name, template in page_name_template.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_author_0, self.user_second)
        self.assertTrue(
            Post.objects.filter(
                image='posts/small.gif'
            ).exists()
        )

    def test_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_posts_group_page_shows_correct_context(self):
        """Шаблон posts/group_list сформирован с правильным контекстом."""

        response = self.client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug"})
        )
        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, "Тестовый текст")
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_author_0, self.user)

    def test_posts_group_page_first_shows_ten_items(self):
        """Шаблон posts/group_list первая страница содержит 10 результатов."""

        response = self.client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug"})
        )
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_posts_group_page_second_shows_two_items(self):
        """Шаблон posts/group_list вторая страница содержит 2 результата."""

        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug"})
            + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 2)

    def test_posts_user_page_shows_correct_context(self):
        """Шаблон posts/group_list сформирован с правильным контекстом."""

        response = self.client.get(
            reverse("posts:profile", kwargs={"username": "TestAuthor"})
        )
        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, "Тестовый текст")
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_author_0, self.user)

    def test_posts_user_page_first_shows_ten_items(self):
        """Шаблон posts/group_list первая страница содержит 10 результатов."""

        response = self.client.get(
            reverse("posts:profile", kwargs={"username": "TestAuthor"})
        )
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_postsuser_page_second_shows_two_items(self):
        """Шаблон posts/group_list вторая страница содержит 2 результата."""

        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": "TestAuthor"})
            + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 2)

    def test_posts_create_page_shows_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    @ classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_posts_group_page_not_include_incorect_post(self):
        """Шаблон group_list не содержит лишний пост."""

        response = self.client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug2"})
        )
        for secong_group_post in response.context["page_obj"]:
            self.assertNotEqual(secong_group_post.pk, self.post[0].pk)

    def test_new_comment_shows_correct_context(self):
        """Новый комментарий коректно отображается на странице поста."""

        comment_text = f"Комментарий от {self.user}"
        form_data = {"text": comment_text}
        response = self.authorized_client.post(
            reverse(
                "posts:add_comment",
                kwargs={"post_id": str(self.post_from_second_group.pk)},
            ),
            data=form_data,
            follow=True,
        )
        response = self.client.get(
            reverse(
                "posts:post_detail",
                kwargs={"post_id": self.post_from_second_group.pk}
            )
        )
        context__first_object = response.context["comments"][0]
        self.assertEqual(context__first_object.author, self.user)
        self.assertEqual(context__first_object.text, comment_text)

    def test_cache_index_page(self):
        """Проверка работы cache на главной странице"""
        post = Post.objects.create(
            text='Текст для проверки работы cache',
            author=self.user)
        added_content = self.authorized_client.get(
            reverse('posts:index')).content
        post.delete()
        deleted_content = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(added_content, deleted_content)
        cache.clear()
        cache_cleared_content = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(added_content, cache_cleared_content)

    def test_page_404(self):
        response = self.authorized_client.get('notexistpage')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_autorized_can_follow_follow(self):
        """Пользователь может подписываться"""
        profile_redirect_address = reverse(
            "posts:profile", kwargs={"username": self.user_second.username}
        )
        response = self.authorized_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.user_second.username},
            )
        )
        self.assertRedirects(response, profile_redirect_address)
        response = self.authorized_client.get(reverse("posts:follow_index"))
        context_first_object = response.context["page_obj"][0]
        self.assertEqual(context_first_object.author, self.user_second)

    def test_autorized_can_unfollow(self):
        """Возможность удалять из подписок других пользователей."""
        profile_redirect_address = reverse(
            "posts:profile", kwargs={"username": self.user_second.username}
        )
        Follow.objects.create(user=self.user, author=self.user_second)
        response = self.authorized_client.get(reverse("posts:follow_index"))
        context_first_object = response.context["page_obj"][0]
        self.assertEqual(context_first_object.author, self.user_second)
        response = self.authorized_client.get(
            reverse(
                "posts:profile_unfollow",
                kwargs={"username": self.user_second.username},
            )
        )
        self.assertRedirects(response, profile_redirect_address)
        response = self.authorized_client.get(
            reverse(
                "posts:profile_unfollow",
                kwargs={"username": self.user_second.username},
            )
        )
        response = self.authorized_client.get(reverse("posts:follow_index"))
        context_len_not_follower = len(response.context["page_obj"])
        self.assertEqual(context_len_not_follower, 0)

    def test_new_post_only_following_feed(self):
        """Новая запись появляется в ленте подписавшихся, но не в чужих"""
        cache.clear()
        response = self.authorized_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.user_second.username},
            )
        )
        response = self.authorized_client.get(reverse("posts:follow_index"))
        context_first_object_follower = response.context["page_obj"][0]
        self.assertEqual(
            context_first_object_follower.author, self.user_second
        )
        response = self.authorized_client_second.get(
            reverse("posts:follow_index")
        )
        context_len_not_follower = len(response.context["page_obj"])
        self.assertEqual(context_len_not_follower, 1)

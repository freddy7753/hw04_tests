from django.test import TestCase, Client
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, User

ONE_POST: int = 1


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.form = PostForm()
        cls.posts_count = Post.objects.count()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.form_data = {
            'text': 'Test post',
            'group': cls.group.id
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверка на создание нового поста"""
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.count(),
            self.posts_count + ONE_POST
        )

    def test_create_post_is_forbidden_for_guest_client(self):
        """Незарегистрированный пользователь не может создать пост"""
        self.guest_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), self.posts_count)

    def test_for_redact_post(self):
        """Тест на редактирование поста"""
        Post.objects.create(
            text='Test',
            group=self.group,
            author=self.user
        )
        post_id = Post.objects.filter(text='Test')[0].id
        post = Post.objects.get(pk=post_id)
        post.text = 'Test POST'
        post.save()
        self.assertEqual(post.text, 'Test POST')
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.user)

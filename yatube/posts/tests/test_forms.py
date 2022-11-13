from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.form = PostForm()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверка на создание нового поста и его редактирование"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Test post',
            'group': self.group.id
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.get(pk=1)
        post.text = 'Test POST'
        post.save()
        self.assertEqual(post.text, 'Test POST')

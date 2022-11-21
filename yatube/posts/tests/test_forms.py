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
        cls.form_data = {
            'text': 'Test post',
            'group': ''
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
        post_id = Post.objects.order_by('-pub_date')[0].id
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'pk': post_id}
        ))
        self.assertEqual(
            Post.objects.count(),
            self.posts_count + ONE_POST
        )
        self.assertEqual(response.context['post'].text, 'Test post')
        self.assertEqual(response.context['post'].group, None)
        self.assertEqual(response.context['post'].author, self.user)

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
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        self.new_post = Post.objects.create(
            text='Test',
            group=self.group,
            author=self.user
        )
        self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.new_post.id}
            ),
            data=self.form_data,
            follow=True
        )
        post_id = Post.objects.order_by('-pub_date')[0].id
        post = Post.objects.get(pk=post_id)
        self.assertEqual(post.text, 'Test post')
        self.assertEqual(post.group, None)
        self.assertEqual(post.author, self.user)

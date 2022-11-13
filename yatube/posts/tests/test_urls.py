from django.test import Client, TestCase
from django.contrib.auth import get_user_model

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_urls_exists_at_desired_location(self):
        """Проверяем адреса на доступность авторизованным клиентом"""
        urls = [
            '/', '/group/test-slug/',
            '/profile/HasNoName/',
            '/posts/1/', '/create/',
            '/posts/1/edit/'
        ]
        for address in urls:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_posts_urls_exists_for_guest_client(self):
        """Проверяем доступность адресов для неавторизованного клиента"""
        urls = [
            '/', '/group/test-slug/',
            '/profile/HasNoName/',
            '/posts/1/'
        ]
        for address in urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_post_create_for_guest_client(self):
        """Проверяем страницу создания поста на redirect"""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, 302)

    def test_post_edit_redirect_for_guest_client(self):
        """Проверяем redirect для неавторизованного клиента"""
        response = self.guest_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, 302)

    def test_for_unexpected_page(self):
        """Проверяем на несуществующую страницу"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """Url-адрес использует соответсвующий шаблон"""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

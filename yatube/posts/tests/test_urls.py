from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


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
        cls.templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html'
        }
        cls.urls_for_guest_client = [
            '/', '/group/test-slug/',
            '/profile/HasNoName/',
            '/posts/1/'
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_urls_exists_at_desired_location(self):
        """Проверяем адреса на доступность авторизованным клиентом"""
        for address in self.templates_url_names.keys():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_urls_exists_for_guest_client(self):
        """Проверяем доступность адресов для неавторизованного клиента"""
        for address in self.urls_for_guest_client:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_for_guest_client(self):
        """Проверяем страницу создания поста на redirect"""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_redirect_for_guest_client(self):
        """Проверяем redirect для неавторизованного клиента"""
        response = self.guest_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_for_unexpected_page(self):
        """Проверяем на несуществующую страницу"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """Url-адрес использует соответсвующий шаблон"""
        for address, template in self.templates_url_names.items():
            """Для авторизованного пользователя"""
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

        for address in self.urls_for_guest_client:
            """Для не авторизованного пользователя"""
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(
                    response, self.templates_url_names[address]
                )

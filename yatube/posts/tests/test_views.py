from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User

NUMBER_OF_POSTS: int = 1


class PostPagesTests(TestCase):
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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL адрес использует свой шаблон"""
        templates_pages_name = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'HasNoName'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'pk': 1}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': 1}): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class ContextTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='user1')
        cls.user2 = User.objects.create_user(username='user2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post1 = Post.objects.create(
            author=cls.user1,
            text='Test post 1',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), NUMBER_OF_POSTS)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'test_slug'}
        ))
        self.assertEqual(response.context['post'].text, 'Test post 1')
        self.assertEqual(response.context['post'].group, self.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'user1'}
        ))
        self.assertEqual(response.context['post'].text, 'Test post 1')
        self.assertEqual(response.context['post'].author, self.user1)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'pk': self.post1.id}
        ))
        self.assertEqual(response.context['post'].text, 'Test post 1')
        self.assertEqual(response.context['post'].author, self.user1)
        self.assertEqual(response.context['post'].id, 1)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        form_data = {'text': 'redact text', 'group': self.group.id}
        self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post1.id}),
            data=form_data, follow=True)
        edit_post = Post.objects.get(id=self.post1.id)
        self.assertEqual(edit_post.text, form_data['text'])

    def test_post_added_correctly(self):
        """Пост при создании добавлен корректно"""
        response_index = self.authorized_client.get(
            reverse('posts:index')
        )
        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug'}
                    )
        )
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': 'user1'}
                    )
        )
        index = response_index.context['post'].text
        group = response_group.context['post'].group
        profile = response_profile.context['post'].author
        self.assertEqual(self.post1.text, index)
        self.assertEqual(self.post1.group, group)
        self.assertEqual(self.post1.author, profile)


class PaginatorViewsTest(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug'
        )
        post_list = []
        for i in range(13):
            post_list.append(Post(
                text=f'Тестовый текст {i}',
                group=self.group,
                author=self.user)
            )
        Post.objects.bulk_create(post_list)

    def test_correct_records_contains_on_page(self):
        """Проверка количества постов на первой и второй странице"""
        postfixurl_posts = [('', 10), ('2', 3)]
        templates_pages_name = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'HasNoName'})
        ]

        for postfixurl, posts in postfixurl_posts:
            for page in templates_pages_name:
                with self.subTest(page=page):
                    response_first_page = self.authorized_client.get(
                        page, {'page': postfixurl}
                    )
                    self.assertEqual(len(
                        response_first_page.context['page_obj']), posts
                    )

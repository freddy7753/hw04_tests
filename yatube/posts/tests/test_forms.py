# import shutil
# import tempfile

# from django.conf import settings
# from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, User

ONE_POST: int = 1
# TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


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
        self.assertEqual(
            response.context['post'].text,
            self.form_data['text']
        )
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
        post_id = Post.objects.first().id
        post = Post.objects.get(pk=post_id)
        self.assertEqual(post.text, self.form_data['text'])
        self.assertEqual(post.group, None)
        self.assertEqual(post.author, self.user)

#     def test_comment_post_is_forbidden_for_guest_client(self):
#         """Не авторизованный пользователь
#          не может комментировать пост"""
#         group = Group.objects.create(
#             title='Тестовая группа',
#             slug='test_slug',
#             description='Тестовое описание'
#         )
#         new_post = Post.objects.create(
#             text='Test',
#             group=group,
#             author=self.user
#         )
#         comment = Comment.objects.count()
#         self.guest_client.post(
#             reverse(
#                 'posts:add_comment',
#                 kwargs={'post_id': new_post.id}
#             ),
#             data={'text': 'Test comment'},
#             follow=True
#         )
#         self.assertEqual(Comment.objects.count(), comment)
#
#     def test_comment_post_for_authorized_client(self):
#         """Комментарий после успешной отправки
#          появляется на странице поста"""
#         group = Group.objects.create(
#             title='Тестовая группа',
#             slug='test_slug',
#             description='Тестовое описание'
#         )
#         new_post = Post.objects.create(
#             text='Test',
#             group=group,
#             author=self.user
#         )
#         self.authorized_client.post(
#             reverse(
#                 'posts:add_comment',
#                 kwargs={'post_id': new_post.id}
#             ),
#             data={'text': 'Test comment for authorized client'},
#             follow=True
#         )
#         self.assertEqual(Comment.objects.count(), 1)
#
# #
# @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
# class PostCreateFormTests(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.user = User.objects.create_user(username='auth')
#         cls.posts_count = Post.objects.count()
#         cls.group = Group.objects.create(
#             title='Тестовая группа',
#             slug='test-slug',
#             description='Тестовое описание',
#         )
#         cls.form = PostForm()
#         cls.small_gif = (
#             b'\x47\x49\x46\x38\x39\x61\x02\x00'
#             b'\x01\x00\x80\x00\x00\x00\x00\x00'
#             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
#             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
#             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
#             b'\x0A\x00\x3B'
#         )
#         cls.uploaded = SimpleUploadedFile(
#             name='small.gif',
#             content=cls.small_gif,
#             content_type='image/gif'
#         )
        # cls.post = Post.objects.create(
        #     author=cls.user,
        #     text='Test post',
        #     group=cls.group,
        #     image=cls.uploaded
        # )
    #
    # @classmethod
    # def tearDownClass(cls):
    #     super().tearDownClass()
    #     shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
    #
    # def setUp(self):
    #     self.authorized_client = Client()
    #     self.authorized_client.force_login(self.user)
    #
    # def test_create_post(self):
    #     """Валидная форма создает запись в Post."""
    #     form_data = {
    #         'text': 'Тестовый пост',
    #         'group': self.group.id,
    #         'image': self.uploaded
    #     }
    #     response = self.authorized_client.post(
    #         reverse('posts:post_create'),
    #         data=form_data,
    #         follow=True,
    #     )
    #     self.assertRedirects(response, reverse(
    #         'posts:profile',
    #         kwargs={'username': 'auth'})
    #                          )
    #     self.assertEqual(
#     Post.objects.count(),
#     self.posts_count + 1)
    #     self.assertIsNotNone(
    #         Post.objects.filter(image='posts/small.gif')
    #     )


# def test_image_post(self):
#     """При выводе поста с картинкой изображение
#     передаётся в словаре"""
#     list_pages_names = (
#         reverse('posts:index'),
#         reverse('posts:post_detail',
#                 kwargs={'pk': '1'}),
#         reverse('posts:profile', kwargs={'username': 'auth'}),
#         reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
#     )
#     for page in list_pages_names:
#         with self.subTest(page=page):
#             response = self.authorized_client.get(page)
#             object_post = response.context['page_obj']
#             print(response.context.keys())
#             self.assertIn(object_post.image, )

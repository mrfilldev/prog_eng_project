from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import Post, Group
from ..forms import PostForm

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='auth'
        )
        cls.group1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug-1',
            description='Тестовое описание 1',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group2,
        )
        cls.form = PostForm()

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_forms_create_post(self):
        """Проверка наличия создания новой записи"""
        posts_count = Post.objects.count()
        group_field = PostFormTests.group2.pk
        text_test = 'Тестовый текст2'
        form_fields = {
            'text': text_test,
            'group': group_field
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_fields,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=PostFormTests.group2.id,
                text=text_test,
            ).exists()
        )

    def test_forms_edit_post(self):
        """Проверка наличия изменения существующей записи"""
        group_field = PostFormTests.group1.pk
        text_test = 'Тестовый текст1'
        form_fields = {
            'text': text_test,
            'group': group_field
        }

        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': PostFormTests.post.pk,
                }
            ),
            data=form_fields,
        )

        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={

                    'post_id': PostFormTests.post.pk,
                }
            ),

        )

        self.assertTrue(
            Post.objects.filter(
                group=PostFormTests.group1.id,
                text=text_test,
            ).exists()
        )


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='auth'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )
        cls.image_post = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.image_post,
            content_type='image/gif'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_PostForm_makes_post_with_image(self):
        """При отправке поста с картинкой через форму PostForm
        создаётся запись в базе данных"""
        self.tasks_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Текст из формы',
            'image': 'small.gif',
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertEqual(Post.objects.count(), self.tasks_count + 1)
        post = Post.objects.latest('pk')
        self.assertEqual(post.text, 'Текст из формы')
        self.assertEqual(post.group, self.group)
        self.assertIsNotNone(post.image)

    def test_index_page_show_image_in_context(self):
        """При выводе поста с картинкой изображение передаётся
        в словаре context на главную страницу"""
        form_data = {
            'group': self.group.id,
            'text': 'Текст из формы',
            'image': 'small.gif',
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            response.context['page_obj'][1].image, self.post.image
        )

    def test_profile_group_list_and_post_detail_show_image_in_context(self):
        """При выводе поста с картинкой изображение передаётся
        в словаре context на страницу профайла, группы и отдельного поста"""
        form_data = {
            'group': self.group.id,
            'text': 'Текст из формы',
            'image': 'small.gif',
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        check_context = (
            reverse('posts:profile', args={self.user.username}),
            reverse('posts:group_list', args={self.group.slug}),
            reverse('posts:post_detail', args={self.post.id})
        )
        for reverse_name in check_context:
            with self.subTest(reverse_name=reverse_name):
                self.authorized_client.get(reverse_name)
        self.assertIsNotNone(self.uploaded)

    def test_cache_index(self):
        """Тест для проверки кеширования главной страницы index."""
        response_predelete = self.client.get(reverse('posts:index'))
        Post.objects.filter(pk=self.post.pk).delete()
        response_deleted = self.client.get(reverse('posts:index'))
        content_deleted = response_deleted.content
        self.assertEqual(response_predelete.content, content_deleted)
        cache.clear()
        response_cached = self.client.get(reverse('posts:index'))
        content_cached = response_cached.content
        self.assertNotEqual(content_deleted, content_cached)

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..models import Post, Group, Comment

User = get_user_model()


class PostsPagesTests(TestCase):
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
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group2,
        )

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_page_show_correct_context(self):
        """Шаблон index с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author.username,
                         self.post.author.username)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group.title, self.post.group.title)

    def test_post_with_the_group_appears_in_index_group_list_profile(self):
        """При создании поста с группой он появляется в index.html,
        group_list.html, profile.html"""
        new_response = (
            reverse('posts:index'),
            reverse('posts:group_list', args={self.post.group.slug}),
            reverse('posts:profile', args={self.post.author.username}),
        )
        for reverse_name in new_response:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn(self.post, (response.context['page_obj']))
        response = self.authorized_client.get(reverse('posts:group_list',
                                                      args={self.group.slug}))
        self.assertNotIn(self.post.id, (response.context['page_obj']))

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edited с правильными полями."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                args={self.post.id}
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
            post_edited = response.context.get('post')
            self.assertEqual(post_edited.text, self.post.text)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create с правильными полями."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.page_obj = []
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test_group_title',
            slug='test_slug',
            description='test_description',
        )
        for i in range(13):
            cls.page_obj.append(
                Post(
                    author=cls.author,
                    text=f'{i} test_text',
                    group=cls.group,
                )
            )
        cls.posts = Post.objects.bulk_create(cls.page_obj)

    def setUp(self):
        # Создаем неавторизованного пользователя
        self.guest_client = Client()

    #        self.authorized_client.force_login(self.user)

    def test_index_first_page_contains_ten_records(self):
        """Тест: на первой странице index должно быть 10 постов."""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_three_records(self):
        """Тест: на второй странице index должно быть три поста."""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_first_page_contains_ten_records(self):
        """Тест: на первой странице group_list должно быть 10 постов."""
        response = self.client.get(reverse('posts:group_list', kwargs={
            'slug': self.group.slug}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_three_records(self):
        """Тест: на второй странице group_list должно быть три поста."""
        response = self.client.get(reverse('posts:group_list', kwargs={
            'slug': self.group.slug}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


class CommentFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='ArtComms')
        cls.group = Group.objects.create(
            title='Название группы для теста3',
            slug='test-slug3',
            description='Описание группы для теста3'
        )
        cls.post = Post.objects.create(
            text='Текст поста для теста3',
            author=cls.user,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст коммента для теста',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_add_comment(self):
        """Валидная форма создает комментарий."""
        form_data = {
            'text': 'Текст коммента для теста',
            'post': self.post,
        }
        # Отправили POST запрос
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.pk}
            ),
            data=form_data
        )
        # Проверили редирект
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            )
        )
        # Проверили, что коммент создан
        self.assertTrue(
            Comment.objects.filter(
                text='Текст коммента для теста',
                post=self.post
            ).exists()
        )

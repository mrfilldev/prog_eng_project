from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def test_str_model_post(self):
        """Проверяем, что у моделей корректно работает str."""
        post = PostModelTest.post
        expected_object_name = post.text
        self.assertEqual(expected_object_name, str(post))

    def test_str_model_group(self):
        """Проверяем, что у моделей корректно работает str."""
        group = self.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_post_verbose_name_label(self):
        """verbose_name поля text совпадает с ожидаемым."""
        post = self.post
        # Получаем из свойста класса Task значение verbose_name для title
        verbose = post._meta.get_field('text').verbose_name
        self.assertEqual(verbose, 'Ваш пост:')

    def test_title_help_text(self):
        """help_text поля text совпадает с ожидаемым."""
        post = self.post
        # Получаем из свойста класса Task значение help_text для title
        help_text = post._meta.get_field('text').help_text
        self.assertEqual(help_text, 'Здесь напишите текст к вашему посту')

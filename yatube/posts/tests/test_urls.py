from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from http import HTTPStatus

from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='HasNoName')

        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_about_author(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_about_tech(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)


class PostsUrlTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.user_author = User.objects.create_user(username='author')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовая текст',
        )
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.user_author)

        cls.code_urls = [
            [HTTPStatus.OK, '/'],
            [HTTPStatus.OK, f'/group/{cls.group.slug}/'],
            [HTTPStatus.OK, f'/profile/{cls.user_author.username}/'],
            [HTTPStatus.OK, f'/posts/{cls.post.id}/'],
            [HTTPStatus.FOUND, f'/posts/{cls.post.id}/edit/'],
            [HTTPStatus.OK, '/create/'],
            [HTTPStatus.NOT_FOUND, '/unexisting_page/'],
        ]

        cls.templates_url_names = [
            ['posts/index.html', '/'],
            ['posts/group_list.html', f'/group/{cls.group.slug}/'],
            ['posts/profile.html', f'/profile/{cls.user_author.username}/'],
            ['posts/post_detail.html', f'/posts/{cls.post.id}/'],
            ['core/404.html', '/unexisting_page/'],
        ]

    def setUp(self):
        self.guest_client = Client()  # не авторизованный
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_edit(self):
        response = self.authorized_client_author.get('/posts/1/edit/')
        self.assertEqual(response.status_code, 200)

    def test_post_create(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_urls_everyone_correct_code(self):
        """URL-адрес отдает нужный код."""
        # Шаблоны по адресам

        for code, address in self.code_urls:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                print(response, code, address)
                self.assertEqual(response.status_code, code)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам

        for template, address in self.templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_task_list_url_redirect(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        print(response)
        self.assertRedirects(
            response, '/auth/login/?next=%2Fcreate%2F'
        )

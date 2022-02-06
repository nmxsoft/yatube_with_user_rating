from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.post_author = User.objects.create_user(username='Author')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.post_author,
        )
        cls.group = Group.objects.create(
            title='Test',
            slug='test',
            description='Test group'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.post_author)

    def test_guest_user_urls(self):
        urls_response_code = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK,
            reverse(
                'posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_slug',
                kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse(
                'posts:group_slug',
                kwargs={'slug': 'slug-not-exist'}): HTTPStatus.NOT_FOUND,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}): HTTPStatus.FOUND,
            reverse(
                'posts:post_create'): HTTPStatus.FOUND,
            '/page-not-exist/': HTTPStatus.NOT_FOUND
        }
        for url, response_code in urls_response_code.items():
            with self.subTest(url=url):
                status_code = self.guest_client.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_authorized_user_urls(self):
        urls_response_code = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK,
            reverse(
                'posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_slug',
                kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse(
                'posts:group_slug',
                kwargs={'slug': 'slug-not-exist'}): HTTPStatus.NOT_FOUND,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}): HTTPStatus.FOUND,
            reverse(
                'posts:post_create'): HTTPStatus.OK,
            '/page-not-exist/': HTTPStatus.NOT_FOUND,
        }
        for url, response_code in urls_response_code.items():
            with self.subTest(url=url):
                status_code = self.authorized_client.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_author_user_urls(self):
        urls_response_code = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK,
            reverse(
                'posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_slug',
                kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse(
                'posts:group_slug',
                kwargs={'slug': 'slug-not-exist'}): HTTPStatus.NOT_FOUND,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}): HTTPStatus.OK,
            reverse(
                'posts:post_create'): HTTPStatus.OK,
            '/page-not-exist/': HTTPStatus.NOT_FOUND,
        }
        for url, response_code in urls_response_code.items():
            with self.subTest(url=url):
                status_code = self.author_client.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_urls_uses_correct_template(self):
        url_templates_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_slug', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
            'page-not-exist': 'core/404.html'
        }
        for address, template in url_templates_names.items():
            with self.subTest(adress=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

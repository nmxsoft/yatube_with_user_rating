from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostsFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Test',
            slug='test_slug',
            description='Test group'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
            'author': self.post.author
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, form_data['author'])
        self.assertEqual(post.group.id, form_data['group'])

    def test_edit_post(self):
        post = Post.objects.create(
            text='Текст поста',
            author=self.user,
            group=self.group,
        )
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
            'author': self.post.author
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                args=[post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, form_data['author'])
        self.assertEqual(post.group.id, form_data['group'])

    def test_create_post_guest(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post_create_redirect = (reverse('users:login') + '?next='
                                + reverse('posts:post_create'))
        self.assertRedirects(response, post_create_redirect)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edit_post_guest(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'новый текст',
            'group': self.group.id
        }
        response = self.client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        post_edit_redirect = (reverse('users:login') + '?next='
                              + reverse('posts:post_edit',
                                        kwargs={'post_id': self.post.pk}))
        self.assertRedirects(response, post_edit_redirect)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertNotEqual(self.post.text, form_data['text'])

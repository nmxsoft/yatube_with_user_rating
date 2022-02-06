from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from yatube.settings import POSTS_PER_SITE

from ..models import Group, Post

User = get_user_model()


class PostsViewsTests(TestCase):
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
        cls.group1 = Group.objects.create(
            title='Test1',
            slug='test1_slug',
            description='Test1 group'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_uses_correct_template(self):
        pages_templates_names = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_slug', kwargs={'slug': 'test_slug'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.post.author}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
        }
        for reverse_name, template in pages_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        context_objects = {
            self.user: first_object.author,
            self.post.text: first_object.text,
            self.group: first_object.group,
            self.post.id: first_object.id,
        }
        for reverse_name, response_name in context_objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    def test_post_posts_group_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_slug', kwargs={'slug': self.group.slug}))
        for post in response.context['page_obj']:
            self.assertEqual(post.group, self.group)

    def test_post_profile_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        for post in response.context['page_obj']:
            self.assertEqual(post.author, self.user)

    def test_post_posts_edit_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_post_detail_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        post_pk = response.context['post'].pk
        self.assertEqual(post_pk, self.post.pk)

    def test_post_post_create_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_new_create(self):
        new_post = Post.objects.create(
            author=self.user,
            text=self.post.text,
            group=self.group
        )
        ver_pages = [
            reverse('posts:index'),
            reverse('posts:group_slug', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})]
        for page in ver_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertIn(
                    new_post, response.context['page_obj']
                )

    def test_post_new_not_in_group(self):
        new_post = Post.objects.create(
            author=self.user,
            text=self.post.text,
            group=self.group
        )
        response = self.authorized_client.get(
            reverse(
                'posts:group_slug',
                kwargs={'slug': self.group1.slug})
        )
        self.assertNotIn(new_post, response.context['page_obj'])


class PaginatorViewsTests(TestCase):
    NUM_PAGES_IN_TEST = 17

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Test',
            slug='test_slug',
            description='Test group'
        )
        cls.post = []
        for i in range(0, cls.NUM_PAGES_IN_TEST):
            cls.post.append(Post(text=f'ТестовыйТекст{i}',
                                 author=cls.user,
                                 group=cls.group))
        Post.objects.bulk_create(cls.post)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_split_paginator_page(self):
        split_pages_list = [
            reverse('posts:index'),
            reverse(
                'posts:group_slug', kwargs={'slug': self.group.slug}),
            reverse(
                'posts:profile', kwargs={'username': self.user.username})
        ]
        for page in split_pages_list:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(len(response.context['page_obj']),
                                 POSTS_PER_SITE
                                 )
        for page in split_pages_list:
            with self.subTest(page=page):
                response = self.authorized_client.get(page + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 self.NUM_PAGES_IN_TEST - POSTS_PER_SITE
                                 )

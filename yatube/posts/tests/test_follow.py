from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post, User

User = get_user_model()


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.author = User.objects.create_user(username='TestFollowUser')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_authorized_client_follow(self):
        follow_count = Follow.objects.count()
        self.author_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.user}
        ))
        follow = Follow.objects.last()
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertEqual(follow.author, self.user)

    def test_authorized_client_unfollow(self):
        Follow.objects.create(
            user=self.user,
            author=self.author,
        )
        follow_count = Follow.objects.count()
        self.authorized_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': self.author}
        ))
        unfollow_count = Follow.objects.count()
        self.assertEqual(follow_count, unfollow_count + 1)

    def test_new_follow_author_post_in_page(self):
        response = self.authorized_client.get(reverse('posts:follow_index'))
        posts_count = len(response.context['page_obj'])
        Follow.objects.create(
            user=self.user,
            author=self.author,
        )
        Post.objects.create(author=self.author, text='Test text')
        response = self.authorized_client.get(reverse('posts:follow_index'))
        posts_new_count = len(response.context['page_obj'])
        self.assertLessEqual(posts_count, posts_new_count)

    def test_unfollow_post_not_in_page(self):
        response = self.author_client.get(reverse('posts:follow_index'))
        posts_count = len(response.context['page_obj'])
        Post.objects.create(author=self.user, text='Test text')
        response = self.author_client.get(reverse('posts:follow_index'))
        posts_new_count = len(response.context['page_obj'])
        self.assertEqual(posts_count, posts_new_count)

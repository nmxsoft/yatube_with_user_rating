from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

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
            text='Тест текст',
        )

    def test_models_have_correct_object_names(self):
        text_title_dict = {
            self.post.text[:15]: str(self.post),
            self.group.title: str(self.group),
        }
        for text_field, str_obj in text_title_dict.items():
            with self.subTest(text_field=text_field):
                self.assertEqual(text_field, str_obj)

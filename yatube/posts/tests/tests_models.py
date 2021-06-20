from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class ModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='RHCP',
            description='music band',
        )

        cls.post = Post.objects.create(
            text='Тестовый текст поста, который больше пятнадцати символов!',
            author=User.objects.create(),
            pub_date='11.04.2021',
            group=cls.group,
        )

    def test_post_str(self):
        post_test_text = str(self.post)
        self.assertEqual(post_test_text, 'Тестовый текст ')

    def test_group_str(self):
        post_test_group = str(self.group)
        self.assertEqual(post_test_group, 'RHCP')

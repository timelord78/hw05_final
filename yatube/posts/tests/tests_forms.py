from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='Tolstoy')
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(
            User.objects.get(username='Tolstoy'))
        Group.objects.create(
            title='My test group',
            slug='mtg',
            description='lalalallalallalalaa',
        )
        Post.objects.create(
            text='тестовый текст поста',
            author=User.objects.get(username='Tolstoy'),
        )

    def test_create_post(self):
        group = Group.objects.get(slug='mtg')
        form_data = {
            'text': 'тестовый текст поста который добавили',
            'group': group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Post.objects.filter(
            text='тестовый текст поста который добавили',
            group=group.id).exists()
        )

    def test_edit_post(self):
        group = Group.objects.get(slug='mtg')
        post = get_object_or_404(Post, text='тестовый текст поста')
        form_data = {
            'text': 'тестовый текст поста который изменили',
            'group': group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:edit', args=(post.author.username, post.pk)),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Post.objects.filter(
            text='тестовый текст поста который изменили',
            group=group.id).exists())

    def test_create_post_with_image(self):
        group = Group.objects.get(slug='mtg')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')
        form_data = {
            'text': 'этот пост с картинкой',
            'group': group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Post.objects.filter(
            image='posts/small.gif'
        ).exists())

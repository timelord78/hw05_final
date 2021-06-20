from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class TestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Red Hot Chilly Peppers',
            slug='RHCP',
            description='Тестовый текст для описания группы'
        )
        Post.objects.create(
            text='тестовый текст поста',
            author=User.objects.create_user(username='Tolstoy')
        )

    def setUp(self):
        self.user = User.objects.create_user(username='Dostoevskiy')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            'index.html': reverse('posts:index'),
            'group.html': reverse('posts:slug', kwargs={'slug': 'RHCP'}),
            'new_post.html': reverse('posts:new_post'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def new_post_correct_context(self):
        response = self.authorized_client.get(reverse('posts:new_post'))
        form_fields = {
            'group': forms.fields.CharField,
            'text': forms.fields.CharField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def group_post_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:slug', kwargs={'slug': 'RHCP'}))
        self.assertEqual(response.context['group'].title,
                         'Red Hot Chilly Peppers')
        self.assertEqual(response.context['group'].slug, 'RHCP')
        self.assertEqual(response.context['group'].description,
                         'Тестовый текст для описания группы')

    def paginator_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.context.get('page').object_list.count(), 10)

    def index_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['object_list'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'тестовый текст поста')

    def group_post_shows_post(self):
        response = self.authorized_client.get(reverse('posts:RHCP'))
        first_object = response.context['object_list'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, 'тестовый текст поста')
        self.assertEqual(post_author_0, 'test_author')
        self.assertEqual(post_group_0, 'RHCP')

    def edit_post_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:edit', kwargs={'username': 'Tolstoy',
                    'post_id': '1'}))
        form_fields = {
            'group': forms.fields.CharField,
            'text': forms.fields.CharField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def profile_author_corect_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Tolstoy'})
        )
        first_object = response.context['object_list'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'тестовый текст поста')

    def post_view_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post', kwargs={'username': 'Tolstoy',
                    'post_id': '1'})
        )
        self.assertEqual(response.context['object_list'].count(), 1)
        first_object = response.context['object_list'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'тестовый текст поста')

    def test_image_index(self):
        response = self.guest_client.get(reverse('posts:index'))
        form_fields = {
            'title': forms.fields.CharField,
            'text': forms.fields.CharField,
            'slug': forms.fields.SlugField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_image_profile(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Tolstoy'}))
        form_fields = {
            'title': forms.fields.CharField,
            'text': forms.fields.CharField,
            'slug': forms.fields.SlugField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

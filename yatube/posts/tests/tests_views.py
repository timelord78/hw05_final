from django import forms
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

User = get_user_model()


class TestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_group = Group.objects.create(
            title='Red Hot Chilly Peppers',
            slug='RHCP',
            description='Тестовый текст для описания группы'
        )
        cls.test_post = Post.objects.create(
            text='тестовый текст поста',
            author=User.objects.create_user(username='Tolstoy')
        )
        cls.user1 = User.objects.create(username='donatello')
        cls.user2 = User.objects.create(username='leonardo')

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Dostoevskiy')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            'index.html': reverse('posts:index'),
            'group.html': reverse(
                'posts:group', kwargs={'slug': self.test_group.slug}),
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
        test_group = Group.objects.filter(slug='RHCP')
        response = self.authorized_client.get(
            reverse('posts:slug', kwargs={'slug': f'{test_group.slug}'}))
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
        test_group = Group.objects.filter(slug='RHCP')
        response = self.authorized_client.get(
            reverse('posts:slug', kwargs={'slug': f'{test_group.slug}'}))
        first_object = response.context['object_list'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, 'тестовый текст поста')
        self.assertEqual(post_author_0, 'test_author')
        self.assertEqual(post_group_0, 'RHCP')

    def edit_post_correct_context(self):
        test_post = Post.objects.filter(text='тестовый текст поста')
        response = self.authorized_client.get(
            reverse('posts:edit', test_post.author, test_post.pk))
        form_fields = {
            'group': forms.fields.CharField,
            'text': forms.fields.CharField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def profile_author_corect_context(self):
        author = get_object_or_404(User, username='Tolstoy')
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': f'{author.username}'})
        )
        first_object = response.context['object_list'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'тестовый текст поста')

    def post_view_correct_context(self):
        test_post = get_object_or_404(Post, author='Tolstoy')
        response = self.authorized_client.get(
            reverse('posts:post', kwargs={
                'username': f'{test_post.author.username}',
                'post_id': f'{test_post.pk}'})
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
        test_post = get_object_or_404(Post, pk=1)
        author = test_post.author
        response = self.authorized_client.get(
            reverse('posts:profile', author.username))
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

    def test_follow(self):
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': f'{self.user1.username}'}))
        follow = Follow.objects.filter(
            user=self.user,
            author=self.user1
        ).exists()
        self.assertTrue(follow)

    def test_unfollow(self):
        Follow.objects.create(
            user=self.user,
            author=self.user1
        )
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': f'{self.user1.username}'}
        ))
        follow = Follow.objects.filter(
            user=self.user,
            author=self.user1
        ).exists()
        self.assertFalse(follow)

    def test_add_comment(self):
        post = self.test_post
        username = post.author.username
        user = self.user
        comment = Comment.objects.filter(author=user).exists()
        self.assertFalse(comment)
        self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={'username': username, 'post_id': post.pk}),
            data={'text': 'Тестовый комментарий!'},
            follow=True)
        comment = Comment.objects.filter(author=user).exists()
        self.assertTrue(comment)

    def test_post_follow(self):
        Follow.objects.create(
            user=self.user,
            author=self.user1
        )

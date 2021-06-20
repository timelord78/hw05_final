from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostUrlsTests(TestCase):
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
            author=User.objects.create_user(username='Tolstoy'),
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Dostoevskiy')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.get(slug='RHCP')
        self.post = Post.objects.get(text='тестовый текст поста')

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_page(self):
        response = self.guest_client.get(f'/group/{self.group.slug}')
        self.assertEqual(response.status_code, 200)

    def test_homepage_for_auth(self):
        response = self.authorized_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_page(self):
        response = self.authorized_client.get(f'/group/{self.group.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_redirect_anonymous(self):
        response = self.guest_client.get('/new/')
        self.assertEqual(response.status_code, 302)

    def test_new_post(self):
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_home_template(self):
        response = self.authorized_client.get('/')
        self.assertTemplateUsed(response, 'index.html')

    def test_group_template(self):
        response = self.authorized_client.get(f'/group/{self.group.slug}')
        self.assertTemplateUsed(response, 'group.html')

    def test_group_template(self):
        response = self.authorized_client.get('/new/')
        self.assertTemplateUsed(response, 'new_post.html')

    def test_profile(self):
        response = self.guest_client.get(f'/{self.post.author}/')
        self.assertEqual(response.status_code, 200)

    def test_author_post(self):
        response = self.guest_client.get(
            f'/{self.post.author}/{self.post.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_guest(self):
        response = self.guest_client.get(
            f'/{self.post.author}/{self.post.pk}/edit/', follow=True)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/{self.post.author}/{self.post.pk}/edit/'
        )

    def test_post_edit_non_author(self):
        response = self.authorized_client.get(
            f'/{self.post.author}/{self.post.pk}/edit/', follow=True)
        self.assertRedirects(response, f'/{self.post.author}/{self.post.pk}/')

    def test_post_edit_author(self):
        self.authorized_client.force_login(User.objects.get(
            username='Tolstoy'))
        response = self.authorized_client.get(
            f'/{self.post.author}/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_correct_template(self):
        self.authorized_client.force_login(User.objects.get(
            username='Tolstoy'))
        response = self.authorized_client.get(
            f'/{self.post.author}/{self.post.pk}/edit/')
        self.assertTemplateUsed(response, 'new_post.html')

    def test_404(self):
        response = self.authorized_client.get('/page/not/found/')
        self.assertEqual(response.status_code, 404)

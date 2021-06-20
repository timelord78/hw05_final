from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']
        labels = {
            'group': 'Группа',
            'text': 'Текст поста',
            'image': 'Картинка'
        }
        help_texts = {
            'group': 'Выберите группу',
            'text': 'Напишите свой пост!',
            'image': 'Отправьте изображение!'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Текст комментария'}
        help_texts = {'text': 'Напишите свой комментарий!'}

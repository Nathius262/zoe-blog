from django import forms

from blogPost.models import BlogPost, Category, Comment
from ckeditor.widgets import CKEditorWidget


class CreateCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name']


class CreateBlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'body', 'image']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control '}),
            # 'category': forms.CheckboxSelectMultiple(attrs={'class': 'radio'}),
            'body': forms.CharField(widget=CKEditorWidget()),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'author': forms.Select(attrs={'class': 'form-control'}),
        }


class EditBlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'body', 'image']

    def save(self, commit=True):
        blog_post = self.instance
        blog_post.title = self.cleaned_data['title']
        blog_post.body = self.cleaned_data['body']

        if self.cleaned_data['image']:
            blog_post.body = self.cleaned_data['body']

        if commit:
            blog_post.save()
        return blog_post


class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name_comment', 'email_comment', 'username_comment', 'content', 'parent')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content', 'parent')

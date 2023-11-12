from django import forms
from app.models import Comment


class CommentModelForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body', )

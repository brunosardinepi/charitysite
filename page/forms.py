from django import forms

from . import models


class PageForm(forms.ModelForm):
    class Meta:
        model = models.Page
        fields = [
            'name',
            'page_slug',
            'category',
            'description',
        ]

class DeletePageForm(forms.ModelForm):
    class Meta:
        model = models.Page
        fields = ['name']

class ManagerInviteForm(forms.Form):
    email = forms.EmailField()
    manager_edit_page = forms.BooleanField(required=False, label='Edit Page')
    manager_delete_page = forms.BooleanField(required=False, label='Delete Page')
    manager_invite_page = forms.BooleanField(required=False, label='Invite users to manage Page')

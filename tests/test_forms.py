import pytest
from django.contrib.auth import get_user_model

from users.forms import CustomUserCreationForm, EmailAuthenticationForm

User = get_user_model()


@pytest.mark.django_db
class TestForms:
    def test_custom_user_creation_form_valid(self):
        form = CustomUserCreationForm(data={
            'username': 'alice',
            'email': 'Alice@Example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        assert form.is_valid() is True
        user = form.save()
        assert user.email == 'alice@example.com'

    def test_custom_user_creation_form_rejects_invalid_password(self):
        form = CustomUserCreationForm(data={
            'username': 'bob',
            'email': 'bob@example.com',
            'password1': '123',
            'password2': '123',
        })
        assert form.is_valid() is False

    def test_custom_user_creation_form_requires_email(self):
        form = CustomUserCreationForm(data={
            'username': 'carol',
            'email': '',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        assert form.is_valid() is False

    def test_email_authentication_form_valid(self):
        user = User.objects.create_user(email='login@example.com', username='loginuser', password='Pass1234!')
        form = EmailAuthenticationForm(data={'username': 'login@example.com', 'password': 'Pass1234!'})
        assert form.is_valid() is True

    def test_email_authentication_form_invalid_password(self):
        User.objects.create_user(email='login2@example.com', username='loginuser2', password='Pass1234!')
        form = EmailAuthenticationForm(data={'username': 'login2@example.com', 'password': 'wrongpass'})
        assert form.is_valid() is False

    def test_email_authentication_form_uses_email_label(self):
        form = EmailAuthenticationForm()
        assert form.fields['username'].label == 'Email'

    def test_email_authentication_form_placeholder_is_present(self):
        form = EmailAuthenticationForm()
        assert 'you@example.com' in form.fields['username'].widget.attrs['placeholder']

    def test_user_creation_form_saves_user(self):
        form = CustomUserCreationForm(data={
            'username': 'dora',
            'email': 'DORA@EXAMPLE.COM',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        assert form.is_valid() is True
        user = form.save()
        assert isinstance(user, User)
        assert user.username == 'dora'

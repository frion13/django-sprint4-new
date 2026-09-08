from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm


User = get_user_model()


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class ProfileEditForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

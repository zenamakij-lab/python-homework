from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import CustomUserCreationForm, EmailAuthenticationForm

User = get_user_model()


class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        customer_group, _ = Group.objects.get_or_create(name='Customers')
        self.object.groups.add(customer_group)
        messages.success(self.request, 'Реєстрацію успішно завершено. Увійдіть до системи.')
        return response


class CustomLoginView(LoginView):
    form_class = EmailAuthenticationForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('books:list')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('books:list')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_groups'] = self.request.user.groups.all()
        return context

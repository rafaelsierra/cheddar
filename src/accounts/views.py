# Create your views here.
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from accounts.forms import RegisterForm
from django.conf import settings

class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'accounts/user_create_form.html'
    success_url = reverse_lazy('accounts:register-success')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        # Enforces users are not active and are not members of staff
        # Unless enabled by settings
        user.is_superuser = False
        user.is_staff = False
        user.is_active = settings.CHEDDAR_DEFAULT_USER_ACTIVE_STATUS
        user.save()
        return super(RegisterView, self).form_valid(form)
    
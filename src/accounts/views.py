# Create your views here.
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from accounts.forms import RegisterForm, AddFolderForm, UnsubscribeFeedForm
from django.conf import settings
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from accounts.models import UserSite, Folder
from django.http.response import HttpResponseNotFound, HttpResponse
import json
from sierra.dj.mixins.forms import JSONFormMixin

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
    
    
    
class ChangeFolder(View):
    # TODO: Use FormView and JSONMixinForm
    
    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ChangeFolder, self).dispatch(*args, **kwargs)
    
    def post(self, *args, **kwargs):
        usersite_id = self.request.POST.get('usersite_id')
        folder_id = self.request.POST.get('folder_id', None)
        try:
            usersite = self.request.user.my_sites.get(id=usersite_id)
            if folder_id:
                folder = self.request.user.folders.get(id=folder_id)
            else: 
                folder = None
        except (UserSite.DoesNotExist, Folder.DoesNotExist), e:
            return HttpResponseNotFound()
        else:
            usersite.folder = folder
            usersite.save()
        return HttpResponse(json.dumps({'success': True}), content_type="application/json")
    


class AddFolderView(JSONFormMixin, FormView):
    form_class = AddFolderForm
    
    def form_valid(self, form):
        Folder.objects.get_or_create(name=form.cleaned_data['name'], user=self.request.user, defaults={'is_active':True})[0]
        return super(AddFolderView, self).form_valid(form)
    
    

class UnsubscribeFeed(JSONFormMixin, FormView):
    form_class = UnsubscribeFeedForm
    def form_valid(self, form):
        site = form.cleaned_data['site']
        usersite = UserSite.objects.get(user=self.request.user, site=site)
        usersite.delete()
        return super(UnsubscribeFeed, self).form_valid(form)
        
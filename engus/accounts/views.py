import datetime
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, DeleteView
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response
from django.contrib.auth import login, authenticate
from django.utils import timezone
from braces.views import LoginRequiredMixin
from engus.cards.models import Card
from .forms import CustomUserCreationForm, CardsGoalCreateForm
from .models import Invite, CardsGoal


class ProfileView(LoginRequiredMixin, TemplateView):

    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        all_cards_learning_by_user = Card.objects.filter(user=self.request.user).learning()
        card_to_repeat_by_user = Card.objects.filter(user=self.request.user).to_repeat()
        context['learned_cards_count'] = all_cards_learning_by_user.count() - card_to_repeat_by_user.count()
        context['most_difficult_cards'] = all_cards_learning_by_user.order_by('-repeat_count')[:10]
        return context


class CardsGoalCreateView(LoginRequiredMixin, FormView):
    form_class = CardsGoalCreateForm
    template_name = 'accounts/cardsgoal_create.html'
    success_url = reverse_lazy('accounts:profile')

    def get(self, request, *args, **kwargs):
        try:
            CardsGoal.objects.get(user=request.user)
            return redirect('accounts:profile')
        except CardsGoal.DoesNotExist:
            return super(CardsGoalCreateView, self).get(self, request, *args, **kwargs)

    def form_valid(self, form):
        now = timezone.now()
        goal = form.save(commit=False)
        goal.start = now
        goal.finish = now + datetime.timedelta(days=form.cleaned_data['days'])
        goal.user = self.request.user
        goal.initial_number = Card.objects.filter(user=self.request.user).learned().count()
        goal.save()
        return super(CardsGoalCreateView, self).form_valid(form)


class CardsGoalDeleteView(LoginRequiredMixin, DeleteView):
    model = CardsGoal
    success_url = reverse_lazy('accounts:profile')

    def get_queryset(self):
        base_qs = super(CardsGoalDeleteView, self).get_queryset()
        return base_qs.filter(user=self.request.user)



@csrf_protect
@never_cache
def register(request):
    if request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                username = form.clean_username()
                password = form.clean_password2()
                user = form.save()
                invite = Invite.objects.get(code=form.cleaned_data['invite_code'])
                invite.registered_user = user
                invite.save()
                authenticated_user = authenticate(username=username, password=password)
                if authenticated_user is not None and authenticated_user.is_active:
                    login(request, authenticated_user)
                return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            form = CustomUserCreationForm()
        return render_to_response('registration/register.html', {'form': form, },
                                  context_instance=RequestContext(request))

from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Cat, Toy, Feeding
from .forms import FeedingForm, RegisterForm
from django.contrib.auth.models import AnonymousUser

# Create your views here.

# Define the home view
class Home(LoginView):
  template_name = 'home.html'

  # def get_context_data(self, **kwargs):
  #   context = super().get_context_data(**kwargs)
  #   context['cats'] = Cat.objects.all()
    
  #   print(context)
  #   if (self.request.user != AnonymousUser()):
  #      context['user_cats'] = Cat.objects.filter(user=self.request.user)
  #      return context
  #   else:
  #      return context

def about(request):
  return render(request, 'about.html')

@login_required
def cat_index(request):
  cats = Cat.objects.filter(user=request.user)
  return render(request, 'cats/index.html', { 'cats': cats })


class CatDetail(LoginRequiredMixin,DetailView):
    model = Cat
    template_name = 'cats/detail.html'
    
    # redirect user to home page if trying to view a cat they didn't make
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.user != self.request.user:
            return redirect('home')
        
        return super().dispatch(request, *args, **kwargs)
    
    # pass in feeding form and toys
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feeding_form'] = FeedingForm()
        cat = Cat.objects.get(id=self.get_object().pk)
        context['toys'] = Toy.objects.exclude(id__in = cat.toys.all().values_list('id'))
        print(f"context {self.get_object().pk}")
        return context

    # posting the feeding form
    def post(self, request, *args, **kwargs):
        cat = self.get_object()  
        form = FeedingForm(request.POST) 

        if form.is_valid():
            meal_text = form.cleaned_data['meal']
            date_text = form.cleaned_data['date']
            Feeding.objects.create(cat=cat, meal=meal_text, date=date_text)
        return redirect('cat-detail', pk=cat.pk)

class CatCreate(LoginRequiredMixin, CreateView):
  model = Cat
  fields = ['name', 'breed', 'description', 'age']

  def form_valid(self, form):
    form.instance.user = self.request.user
    return super().form_valid(form)

class CatUpdate(LoginRequiredMixin, UpdateView):
  model = Cat
  fields = ['breed', 'description', 'age']

class CatDelete(LoginRequiredMixin, DeleteView):
  model = Cat
  success_url = '/cats/'

class ToyCreate(LoginRequiredMixin, CreateView):
  model = Toy
  fields = '__all__'


class ToyList(LoginRequiredMixin, ListView):
  model = Toy

class ToyDetail(LoginRequiredMixin, DetailView):
  model = Toy

class ToyUpdate(LoginRequiredMixin, UpdateView):
  model = Toy
  fields = ['name', 'color']

class ToyDelete(LoginRequiredMixin, DeleteView):
  model = Toy
  success_url = '/toys/'

@login_required
def associate_toy(request, cat_id, toy_id):
  Cat.objects.get(id=cat_id).toys.add(toy_id)
  return redirect('cat-detail', pk=cat_id)

@login_required
def remove_toy(request, cat_id, toy_id):
  cat = Cat.objects.get(id=cat_id)
  toy = Toy.objects.get(id=toy_id)
  cat.toys.remove(toy)
  return redirect('cat-detail', pk=cat.id)

def signup(request):
    error_message = ''
    if request.method == 'POST':
        # This is how to create a 'user' form object
        # that includes the data from the browser
        form = RegisterForm(request.POST)
        if form.is_valid():
            # This will add the user to the database
            user = form.save()
            # This is how we log a user in
            login(request, user)
            return redirect('cat-index')
        else:
            error_message = 'Invalid sign up - try again'
    # A bad POST or a GET request, so render signup.html with an empty form
    form = RegisterForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)
    # Same as: 
    # return render(
    #     request, 
    #     'signup.html',
    #     {'form': form, 'error_message': error_message}
    # )

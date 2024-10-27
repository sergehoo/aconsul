from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import render, get_object_or_404, redirect
from django.template import Context
from django.urls import reverse
from django.views.generic import TemplateView, DetailView, FormView
from django.views.generic.detail import SingleObjectMixin

from webhome.forms import CommentForm, ContactForm
from webhome.models import Article, Comment, NosServices, Category


# Create your views here.

class HomePageView(TemplateView):
    template_name = "web/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add forms to context

        context['articles'] = Article.objects.filter(published=True)
        context['services'] = NosServices.objects.all()
        context['contactform'] = ContactForm()

        return context

    # # Call the parent class's dispatch method for normal view processing.
    #     return super().dispatch(request, *args, **kwargs)
    #
    # def dispatch(self, request, *args, **kwargs):
    #     # Call the parent class's dispatch method for normal view processing.
    #     response = super().dispatch(request, *args, **kwargs)
    #
    #     # Check if the user is authenticated. If not, redirect to the login page.
    #     if not request.user.is_authenticated:
    #         return redirect('login')
    #
    #     # Check if the user is a member of the RH Managers group
    #     if request.user.groups.filter(name='ressources_humaines').exists():
    #         # Redirect the user to the RH Managers dashboard
    #         return redirect('rhdash')
    #
    #     # Check if the user is a member of the RH Employees group
    #     elif request.user.groups.filter(name='project').exists():
    #         # Redirect the user to the RH Employees dashboard
    #         return redirect('rh_employee_dashboard')
    #
    #     # If the user is not a member of any specific group, return a forbidden response
    #     else:
    #         return redirect('page_not_found')
    #         # return HttpResponseForbidden("You don't have permission to access this page.")


# Vue pour afficher l'article et ses commentaires
class ArticleDetailView(DetailView):
    model = Article
    template_name = 'web/article_detail.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        # Récupérer uniquement les commentaires de premier niveau (parent=None)
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(parent=None)
        context['comment_form'] = CommentForm()
        return context


# Vue pour ajouter un commentaire ou une réponse
class ArticleCommentView(SingleObjectMixin, FormView):
    model = Article
    form_class = CommentForm
    template_name = 'web/article_detail.html'

    def form_valid(self, form):
        article = self.get_object()
        # Associer l'article et l'utilisateur au commentaire
        comment = form.save(commit=False)
        comment.article = article
        comment.user = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        article = self.get_object()
        return reverse('article_detail', kwargs={'pk': article.pk})


# Combiner les deux vues dans une seule vue
class ArticleDetailCommentView(DetailView, FormView):
    model = Article
    template_name = 'web/article_detail.html'
    context_object_name = 'article'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        # Récupérer les commentaires de premier niveau (parent=None)
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(parent=None)
        return context

    def form_valid(self, form):
        # Récupérer l'article
        article = self.get_object()
        # Créer un nouveau commentaire ou une réponse
        comment = form.save(commit=False)
        comment.article = article
        comment.user = self.request.user

        # Associer le parent si l'utilisateur répond à un commentaire
        parent_id = self.request.POST.get('parent')
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
            comment.parent = parent_comment

        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        # Rediriger vers l'article après la soumission
        return reverse('article_detail', kwargs={'pk': self.object.pk})


class ServiceDetailView(DetailView):
    model = NosServices
    template_name = 'web/service_detail.html'
    context_object_name = 'service'

    def get_context_data(self, **kwargs):
        # Récupérer les commentaires de premier niveau (parent=None)
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


# def contact_view(request):
#     if request.method == 'POST':
#         form = ContactForm(request.POST)
#         if form.is_valid():
#             # Si vous voulez sauvegarder dans la base de données
#             form.save()
#
#             # Envoyer l'email de confirmation
#             send_mail(
#                 form.cleaned_data['subject'],
#                 form.cleaned_data['message'],
#                 form.cleaned_data['email'],
#                 ['contact@afriqconsulting.com'],  # Votre adresse email
#                 fail_silently=False,
#             )
#
#             # Message de confirmation
#             messages.success(request, 'Votre message a été envoyé avec succès !')
#
#             return redirect('contact')  # Rediriger vers la page de contact ou autre
#     else:
#         form = ContactForm()
#
#     return render(request, 'web/contact.html', {'form': form})


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()

            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            user_email = form.cleaned_data['email']

            email = EmailMessage(
                subject,
                message,
                'contact@afriqconsulting.com',  # Expéditeur autorisé
                ['contact@afriqconsulting.com'],
                headers={'Reply-To': user_email}  # Répondre à l'utilisateur
            )
            email.send(fail_silently=False)

            messages.success(request, 'Votre message a été envoyé avec succès !')
            return redirect('contact')

    else:
        form = ContactForm()
    return render(request, 'web/contact.html', {'form': form})

from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, DetailView

from app.forms import CommentModelForm
from app.models import *


class ProductListView(ListView):
    template_name = 'app/product_list.html'
    model = Product


def logout_user(request):
    logout(request)
    return redirect('product_list')


class RegisterUserView(CreateView):
    template_name = 'app/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('product_list')

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        user = User.objects.get(username=request.POST.get('username'))
        Cart.objects.create(user=user)
        return redirect('product_list')


class UserLoginView(LoginView):
    template_name = 'app/login.html'
    form_class = AuthenticationForm
    next_page = reverse_lazy('product_list')


class UserProfileView(ListView):
    template_name = 'app/profile.html'
    context_object_name = 'product_list'

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.get(user=user).product_list.all()


class CartView(ListView):
    template_name = 'app/cart.html'
    context_object_name = 'product_list'

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.get(user=user).product_list.all()


def add_product(request, product_id):
    if request.method == 'GET':
        Cart.objects.get(user=request.user).product_list.add(
            Product.objects.get(id=product_id)
        )
    return redirect('product_list')


def remove_from_cart(request, slug):
    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, slug=slug)
    cart.product_list.remove(product)
    return redirect('cart')


def buy_products(request):
    if request.method == 'GET':
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        bh = BuyHistory.objects.create(user=user)
        bh.product_list.set(cart.product_list.all())
        cart.product_list.clear()
        return redirect('cart')


class BuyHistoryListView(ListView):
    template_name = 'app/buy_history.html'
    context_object_name = 'history_list'

    def get_queryset(self):
        user = self.request.user
        return BuyHistory.objects.filter(user=user)


class ProductDetailView(DetailView):
    template_name = 'app/product_detail.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentModelForm()

        comments = Comment.objects.filter(product=self.get_object())
        context['comment_list'] = comments

        return context


def add_comment(request, slug):
    if request.method == 'POST':
        user = request.user
        product = get_object_or_404(Product, slug=slug)
        form = CommentModelForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = user
            comment.product = product
            comment.save()
            return redirect('product_detail', slug=slug)


def like_product(request, slug):
    user = request.user
    product = get_object_or_404(Product, slug=slug)
    like, created = Like.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(Product),
        object_id=product.id,
        user=user
    )
    try:
        dislike = Dislike.objects.get(
            content_type=ContentType.objects.get_for_model(Product),
            object_id=product.id,
            user=user
        )
        dislike.delete()
    except Dislike.DoesNotExist:
        pass
    if created or like.disliked:
        like.disliked = False
        like.save()
        return redirect('product_list')
    else:
        like.delete()
        return redirect('product_list')


def dislike_product(request, slug):
    user = request.user
    product = get_object_or_404(Product, slug=slug)
    dislike, created = Dislike.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(Product),
        object_id=product.id,
        user=user
    )
    try:
        like = Like.objects.get(
            content_type=ContentType.objects.get_for_model(Product),
            object_id=product.id,
            user=user
        )
        like.delete()
    except Like.DoesNotExist:
        pass
    if created or not dislike.liked:
        dislike.liked = True
        dislike.save()
        return redirect('product_list')
    else:
        dislike.delete()
        return redirect('product_list')


def like_comment(request, pk):
    user = request.user
    comment = get_object_or_404(Comment, pk=pk)
    like, created = Like.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(Comment),
        object_id=comment.id,
        user=user
    )
    try:
        dislike = Dislike.objects.get(
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=comment.id,
            user=user
        )
        dislike.delete()
    except Dislike.DoesNotExist:
        pass
    if created or like.disliked:
        like.disliked = False
        like.save()
        slug = comment.product.slug
        return redirect('product_detail', slug=slug)
    else:
        like.delete()
        slug = comment.product.slug
        return redirect('product_detail', slug=slug)


def dislike_comment(request, pk):
    user = request.user
    comment = get_object_or_404(Comment, pk=pk)
    dislike, created = Dislike.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(Comment),
        object_id=comment.id,
        user=user
    )
    try:
        like = Like.objects.get(
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=comment.id,
            user=user
        )
        like.delete()
    except Like.DoesNotExist:
        pass
    if created or not dislike.liked:
        dislike.liked = True
        dislike.save()
        slug = comment.product.slug
        return redirect('product_detail', slug=slug)
    else:
        dislike.delete()
        slug = comment.product.slug
        return redirect('product_detail', slug=slug)

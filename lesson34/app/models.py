from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Like(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    disliked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('content_type', 'object_id', 'user')

    def __str__(self):
        return f"{self.content_type} - {self.object_id}"


class Dislike(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('content_type', 'object_id', 'user')

    def __str__(self):
        return f"{self.content_type} - {self.object_id}"


class Product(models.Model):
    title = models.CharField(max_length=255)
    categories = models.ManyToManyField(Category)
    price = models.PositiveIntegerField()
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField()
    likes = GenericRelation(Like)
    dislike = GenericRelation(Dislike)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} - {self.price}"

    def get_absolute_url(self):
        return reverse('remove_from_cart', args=(self.slug, ))

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        str_ = f"{self.title}-{self.price}"
        self.slug = slugify(str_)
        super(Product, self).save(force_insert=False, force_update=False, using=None, update_fields=None)


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                null=True, blank=True)
    product_list = models.ManyToManyField(Product)

    def get_total_price(self):
        return self.product_list.all().aggregate(Sum('price'))

    def __str__(self):
        if not self.user:
            return 'empty_user'
        return self.user.username


class BuyHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    product_list = models.ManyToManyField(Product)
    buy_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    published = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    likes = GenericRelation(Like)
    dislike = GenericRelation(Dislike)

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"

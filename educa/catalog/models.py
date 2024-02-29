from django.contrib.auth.models import User
from django.db import models


class Product(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=64, unique=True)
    date_time_started = models.DateTimeField(null=True, blank=True)
    price = models.IntegerField(default=0)
    max_group_size = models.IntegerField(null=True, blank=True)
    min_group_size = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.author} {self.product_name} {self.date_time_started} {self.price} {self.min_group_size} {self.max_group_size}'

    @property
    def count_lessons(self):
        lessons = self.lessons.all()
        cnt = lessons.count
        return cnt

    @property
    def date_started(self):
        return (self.date_time_started).strftime("%d.%m.%Y %H:%M")


class ProductAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='accesses')

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user} {self.product}'


class Lesson(models.Model):
    lesson_name = models.CharField(max_length=128)
    video_url = models.URLField()
    product = models.ForeignKey(Product, related_name='lessons', on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.lesson_name} {self.video_url} {self.product}'


class ProductGroup(models.Model):
    group_name = models.CharField(max_length=64)
    students = models.ManyToManyField(User)
    product = models.ForeignKey(Product, related_name='groups', on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.group_name} {self.product.product_name}'

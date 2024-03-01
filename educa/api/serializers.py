from rest_framework import serializers
from catalog.models import Product, ProductGroup, ProductAccess, Lesson


# class StudentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ("id", "username", )


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "lesson_name", "video_url", )


class ProductsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    author = serializers.CharField()
    product_name = serializers.CharField()
    total_lessons = serializers.IntegerField()
    price = serializers.IntegerField()
    date_time_started = serializers.DateTimeField(format='%Y-%m-%d %H:%M')

    class Meta:
        model = Product
        fields = ("id", "author", "product_name", "total_lessons",  "date_time_started", "price")


class ProductDetailSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True)
    date_started = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ("id", "author", "product_name", "lessons",  "date_started", "price")


class GroupSerializer(serializers.ModelSerializer):
    total_members = serializers.IntegerField()

    class Meta:
        model = ProductGroup
        fields = ("id", "group_name", "total_members", )



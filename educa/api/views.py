from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count, F, Q, ExpressionWrapper, Func
from django.db.models.functions import Cast
from django.http import Http404, JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import APIView
from catalog.models import Product, ProductGroup, ProductAccess, Lesson

from api.serializers import ProductsSerializer, LessonSerializer, ProductDetailSerializer, GroupSerializer
from catalog.signals import random_code


class ProductsList(APIView):
    def get(self, request, format=None):
        data = (Product.objects.all()
                .annotate(total_lessons=Count('lessons'))
                .values("id", "author__username", "product_name", "total_lessons", "price", "date_time_started")
                .order_by('id')
                .annotate(author=F("author__username")))

        serializer = ProductsSerializer(data, many=True)

        return Response(serializer.data)


class ProductDetailView(APIView):
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.request.user.id
        product = self.get_object(pk)
        access = product.accesses.values_list("user", flat=True)
        if user in access or self.request.user.is_superuser:
            serializer = ProductDetailSerializer(product, )
            return Response(serializer.data)
        return Response({"Error": "You don`t have access to the product"}, status=status.HTTP_403_FORBIDDEN)


class ProductGroupsView(APIView):
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        data = (Product.objects.filter(id=pk)
                .annotate(total_members=Count('groups__students'))
                .values("groups__id","groups__group_name", "total_members")
                .annotate(
                    id=F("groups__id"),
                    group_name=F("groups__group_name")
                ))
        serializer = GroupSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GroupsRefactorView(APIView):
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        product = self.get_object(pk)
        if product.get_course_is_started:
            return Response(data={"Error": "Course is started. Refactor groups impossible!"})

        users_access = list(product.accesses.values_list("user__id", flat=True))
        max_size = product.max_group_size

        data_groups = (Product.objects.filter(id=pk)
                    .annotate(total_members=Count('groups__students'))
                    .values("groups__id", "total_members"))

        after_removed = list(data_groups.values_list("groups__id", flat=True))

        groups = {}

        for group in data_groups:
            groups[f'{group["groups__id"]}'] = group["total_members"]

        sum_group_value = sum(groups.values())

        if sum_group_value % max_size == 0:
            print("группы будут под завязку")
            new_groups = {}
            total_group = sum_group_value // max_size

            for i in range(total_group):
                number_for_new_group = random_code()
                product_name = f'{product.product_name}_{number_for_new_group}'
                group = ProductGroup.objects.create(group_name=product_name, product=product)
                group.save()
                new_groups[f"{group.id}"] = []

            keys = list(new_groups.keys())

            for key in keys:
                new_groups[f"{key}"].append(users_access[:max_size])
                del users_access[:max_size]

            for group_id, user_ids in new_groups.items():
                users = User.objects.filter(id__in=user_ids[0])
                group = ProductGroup.objects.get(id=group_id)
                group.students.add(*users)

            ProductGroup.objects.filter(id__in=after_removed).delete()
        else:
            new_groups = {}
            print("группы будут НЕ под завязку")
            total_group = sum_group_value // max_size + 1

            for i in range(total_group):
                number_for_new_group = random_code()
                product_name = f'{product.product_name}_{number_for_new_group}'
                group = ProductGroup.objects.create(group_name=product_name, product=product)
                group.save()
                new_groups[f"{group.id}"] = []

            keys = list(new_groups.keys())

            while len(users_access) != 0:
                for key in keys:
                    try:
                        new_groups[f"{key}"].append(users_access[0])
                        del users_access[0]
                    except IndexError:
                        pass

            for group_id, user_ids in new_groups.items():
                users = User.objects.filter(id__in=user_ids)
                group = ProductGroup.objects.get(id=group_id)
                group.students.add(*users)

            ProductGroup.objects.filter(id__in=after_removed).delete()

        data = {"Success": "Groups successfully formatted"}
        return Response(data, status=status.HTTP_200_OK)


class Round(Func):
    function = 'ROUND'
    arity = 2


class StatisticsView(APIView):
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        users = User.objects.all().exclude(id=1).count()
        product = Product.objects.filter(id=pk)
        total_groups = self.get_object(pk).groups.all().count()

        data = (product.annotate(
                    total=Count("accesses__user", distinct=True),
                    percent=F("total") + users,
                    group_size=F("max_group_size"))
                .annotate(
                    groups_cnt=Count("groups", distinct=True)
                )
                .annotate(
                    medium_group=Cast(F("total") / float(total_groups), models.FloatField()),
                )
                .annotate(
                    group_occupancy_percentage=Cast(Round(F("medium_group") / F("group_size") * 100, 2), models.FloatField())
                )
                .annotate(
                    product_purchase_percentage=Cast(Round(F("total") / float(users) * 100, 2), models.FloatField())
                )
                .values("product_name", "total", "group_occupancy_percentage", "product_purchase_percentage"))

        # print(data)
        return Response(data, status=status.HTTP_200_OK)

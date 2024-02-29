from django.contrib.auth.models import User
from django.db.models import Count, F, Q
from django.http import Http404
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import APIView
from catalog.models import Product, ProductGroup, ProductAccess, Lesson

from api.serializers import ProductsSerializer, LessonSerializer, ProductDetailSerializer


class ProductsList(APIView):
    def get(self, request, format=None):
        data = (Product.objects.all()
                .annotate(total_lessons=Count('lessons'))
                .values("id", "author__username", "product_name", "total_lessons", "price", "date_time_started").order_by('id')
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
        access = self.get_object(pk).accesses.values_list("user", flat=True)
        if user in access or self.request.user.is_superuser:
            serializer = ProductDetailSerializer(product, )
            return Response(serializer.data)
        return Response({"Error": "You don`t have access to the product"}, status=status.HTTP_403_FORBIDDEN)

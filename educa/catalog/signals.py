import random

from django.db.models import Count, Q
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from catalog.models import ProductAccess, ProductGroup


def random_code():
    random.seed()
    return random.randint(1000, 9999)

@receiver(post_save, sender=ProductAccess)
def created_access(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        user = instance.user
        number_for_new_group = random_code()
        # print(product)
        group_max = product.max_group_size
        group_min = product.min_group_size
        print(group_max)
        groups = ProductGroup.objects.filter(product=product)
        if len(groups) <= 0:
            product_name = f'{instance.product.product_name}_{number_for_new_group}'
            group = ProductGroup.objects.create(group_name=product_name, product=product)
            group.students.add(user)
            group.save()
        else:
            started_groups = (ProductGroup.objects.filter(product=product)
                      .annotate(cnt=Count('students'))
                      .exclude(Q(cnt__gte=group_max)))

            if len(started_groups) <= 0:
                product_name = f'{instance.product.product_name}_{number_for_new_group}'
                group = ProductGroup.objects.create(group_name=product_name, product=product)
                group.students.add(user)
                group.save()
            else:
                data_groups = {}
                for group in started_groups:
                    data_groups[f'{group.id}'] = group.cnt

                min_group_value = min(data_groups.values(), key=lambda group_size: group_size)
                min_group_id = min(data_groups.keys(), key=lambda group_id: group_id)
                product_name = f'{instance.product.product_name}_{number_for_new_group}'
                group = ProductGroup.objects.get(id=min_group_id)
                group.students.add(user)
                group.save()



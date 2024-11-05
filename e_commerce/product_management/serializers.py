from rest_framework import serializers
from .models import Product, Categories, Review


class CategoriesSerializer(serializers.ModelSerializer):
    full_path = serializers.SerializerMethodField()

    class Meta:
        model = Categories
        fields = ['id', 'name', 'parent', 'full_path']

    def get_full_path(self, obj):
        full_path = [obj.name]
        parent = obj.parent
        while parent is not None:
            full_path.append(parent.name)
            parent = parent.parent
        return ' > '.join(full_path[::-1])
    

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['product', 'user', 'rating', 'comment', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Categories.objects.all())
    seller = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'seller', 'category', 'stock', 'is_active', 'created_at', 'updated_at']

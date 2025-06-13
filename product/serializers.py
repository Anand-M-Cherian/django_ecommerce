from rest_framework import serializers
from product.models import Product, ProductImages, ProductReviews

class ProductImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProductImages
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):

    images = ProductImageSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField(method_name='get_reviews', read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'brand', 'rating', 'category', 'stock', 'user', 'images', 'reviews')
        extra_kwargs = {
            'name': {'required': True, 'allow_blank': False},
            'description': {'required': True, 'allow_blank': False},
            'brand': {'required': True, 'allow_blank': False},
            'category': {'required': True, 'allow_blank': False},
        }

    def get_reviews(self, obj):
        reviews = obj.reviews.all()
        reviewSerializer = ProductReviewSerializer(reviews, many=True)
        return reviewSerializer.data

class ProductReviewSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProductReviews
        fields = "__all__"
        extra_kwargs = {
            'rating': {'required': True, 'allow_null': False},
            'comment': {'required': True, 'allow_blank': False},
        }
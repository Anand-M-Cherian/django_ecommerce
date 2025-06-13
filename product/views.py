from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from .models import Product, ProductImages, ProductReviews
from rest_framework.response import Response
from .serializers import ProductSerializer, ProductImageSerializer, ProductReviewSerializer
from django.shortcuts import get_object_or_404
from .filters import ProductFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Avg

# Create your views here.

@api_view(['GET'])
def get_products(request):
    productsQuerySet = Product.objects.all().order_by('id')
    productFilterSet = ProductFilter(request.GET, queryset=productsQuerySet)
    count = productFilterSet.qs.count()

    # Pagination
    count_per_page = 2
    paginator = PageNumberPagination()
    paginator.page_size = count_per_page
    finalQueryset = paginator.paginate_queryset(productFilterSet.qs, request)

    productSerializer = ProductSerializer(finalQueryset, many=True)
    return Response({
        "products": productSerializer.data,
        "count": count,
        "count_per_page": count_per_page,
        "total_pages": paginator.page.paginator.num_pages,
        "current_page": paginator.page.number
    })

@api_view(['GET'])
def get_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    productSerializer = ProductSerializer(product, many=False)
    return Response({ "product": productSerializer.data })

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def upload_product_images(request):
    data = request.data
    files = request.FILES.getlist('images')
    product_id = data.get('product')

    # Validate product
    product = get_object_or_404(Product, pk=product_id)

    images = []
    for file in files:
        image = ProductImages.objects.create(product=product, image=file)
        images.append(image)

    imageSerializer = ProductImageSerializer(images, many=True)

    return Response(imageSerializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_product(request):
    data = request.data
    productSerializer = ProductSerializer(data=data)
    if productSerializer.is_valid():
        product = Product.objects.create(**data, user=request.user)
        productSerializer = ProductSerializer(product, many=False)
        return Response({"product": productSerializer.data})
    else:
        return Response(productSerializer.errors, status=400)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    data = request.data

    # Ensure that the user is the owner of the product
    if product.user != request.user:
        return Response({"error": "You do not have permission to update this product"}, status=status.HTTP_403_FORBIDDEN)

    productSerializer = ProductSerializer(product, data=data, partial=True)
    if productSerializer.is_valid():
        productSerializer.save()
        return Response({"product": productSerializer.data})
    else:
        return Response(productSerializer.errors, status=400)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # Ensure that the user is the owner of the product
    if product.user != request.user:
        return Response({"error": "You do not have permission to delete this product"}, status=status.HTTP_403_FORBIDDEN)

    args = {'product': pk}
    images = ProductImages.objects.filter(**args)
    for image in images:
        image.delete()

    product.delete()
    return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    data = request.data
    user = request.user

    # Ensure that the user is not the owner of the product
    if product.user == user:
        return Response({"error": "You cannot review your own product"}, status=status.HTTP_403_FORBIDDEN)

    # Validate rating
    rating = data.get('rating')
    try:
        rating = float(rating)
    except (TypeError, ValueError):
        return Response({"error": "Rating must be a number."}, status=status.HTTP_400_BAD_REQUEST)
    if rating < 0 or rating > 10:
        return Response({"error": "Rating must be between 0 and 10."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if a review by this user for this product already exists
    review, created = ProductReviews.objects.get_or_create(product=product, user=user)

    data['product'] = product.id
    data['user'] = user.id

    reviewSerializer = ProductReviewSerializer(review, data=data, partial=True)
    if reviewSerializer.is_valid():
        reviewSerializer.save()

        # Recalculate and update the product's average rating
        avg_rating = ProductReviews.objects.filter(product=product).aggregate(avg=Avg('rating'))['avg'] or 0
        product.rating = round(avg_rating, 2)
        product.save(update_fields=['rating'])

        if created:
            return Response({"review": reviewSerializer.data, "message": "Review created."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"review": reviewSerializer.data, "message": "Review updated."}, status=status.HTTP_200_OK)
    else:
        return Response(reviewSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    user = request.user

    # Ensure that the user is the owner of the review
    review = get_object_or_404(ProductReviews, product=product, user=user)
    review.delete()

    # Recalculate and update the product's average rating
    avg_rating = ProductReviews.objects.filter(product=product).aggregate(avg=Avg('rating'))['avg'] or 0
    product.rating = round(avg_rating, 2)
    product.save(update_fields=['rating'])
    return Response({"message": "Review deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
import os
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from order.serializers import OrderSerializer
from product.models import Product
from .models import Order, OrderItem, PaymentMethod, OrderStatus, PaymentStatus
from order.filters import OrderFilter
from rest_framework.pagination import PageNumberPagination
import stripe
from utils.helpers import get_current_host
from product.models import Product
from django.contrib.auth.models import User
import logging

# Set up logging
logger = logging.getLogger(__name__)
# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    user = request.user
    data = request.data

    # Validate that order_items are provided
    order_items = data.get('order_items', [])
    if not order_items:
        return Response({"detail": "No order items provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Get payment method from payload or use default
    payment_method = data.get('payment_method', PaymentMethod.CREDIT_CARD)

    # Validate payment method
    if payment_method not in PaymentMethod.values:
        return Response({"detail": f"Invalid payment_method: {payment_method}"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create the order with a temporary total_amount
    order = Order.objects.create(
        user=user,
        street=data.get('street', ''),
        city=data.get('city', ''),
        state=data.get('state', ''),
        zip_code=data.get('zip_code', ''),
        phone_number=data.get('phone_number', ''),
        country=data.get('country', ''),
        total_amount=0,  # Will update after calculating
        payment_method=payment_method,
    )

    total_amount = 0
    for order_item in order_items:

        # Validate that each order_item has a valid product ID
        try:
            product = Product.objects.get(id=order_item['product'])
        except Product.DoesNotExist:
            order.delete()  # Clean up the created order
            return Response({"detail": f"Product with id {order_item['product']} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate stock availability
        quantity = order_item.get('quantity', 1)
        if product.stock < quantity:
            order.delete()
            return Response({"detail": f"Insufficient stock for product '{product.name}'."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the order item
        OrderItem.objects.create(
            order=order,
            product=product,
            name=product.name,
            quantity=quantity,
            price=product.price
        )

        # Update product stock
        product.stock -= quantity
        product.save()

        # Add to total amount
        total_amount += product.price * quantity

    # Update the order's total_amount
    order.total_amount = total_amount
    order.save(update_fields=['total_amount'])

    orderSerializer = OrderSerializer(order, many=False)
    return Response(orderSerializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    user = request.user
    orderQuerySet = Order.objects.filter(user=user).order_by('-created_at')

    if not orderQuerySet.exists():
        return Response({"detail": "No orders found for {} {}".format(user.first_name, user.last_name)}, status=status.HTTP_404_NOT_FOUND)
    
    # Apply filtering if needed (e.g., by payment status, order status, etc.)
    orderFilterSet = OrderFilter(request.GET, queryset=orderQuerySet)
    count = orderFilterSet.qs.count()

    # Apply pagination
    count_per_page = 2
    paginator = PageNumberPagination()
    paginator.page_size = count_per_page
    finalQueryset = paginator.paginate_queryset(orderFilterSet.qs, request)

    orderSerializer = OrderSerializer(finalQueryset, many=True)
    return Response({
        "orders": orderSerializer.data,
        "count": count,
        "count_per_page": count_per_page,
        "total_pages": paginator.page.paginator.num_pages,
        "current_page": paginator.page.number
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order(request, pk):
    user = request.user
    order = get_object_or_404(Order, id=pk)

    if order.user != user:
        return Response({"detail": "You do not have permission to view this order."}, status=status.HTTP_403_FORBIDDEN)

    orderSerializer = OrderSerializer(order, many=False)
    return Response(orderSerializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def process_order(request, pk):
    user = request.user
    order = get_object_or_404(Order, id=pk)

    if order.user != user:
        return Response({"detail": "You do not have permission to process this order."}, status=status.HTTP_403_FORBIDDEN)

    data = request.data

    # Validate order_status if provided
    order_status = data.get('order_status')
    if order_status and order_status not in OrderStatus.values:
        return Response({"detail": f"Invalid order_status: {order_status}"}, status=status.HTTP_400_BAD_REQUEST)

    # Validate payment_status if provided
    payment_status = data.get('payment_status')
    if payment_status and payment_status not in PaymentStatus.values:
        return Response({"detail": f"Invalid payment_status: {payment_status}"}, status=status.HTTP_400_BAD_REQUEST)

    # Use serializer for partial update
    serializer = OrderSerializer(order, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_order(request, pk):
    user = request.user
    order = get_object_or_404(Order, id=pk)

    if order.user != user:
        return Response({"detail": "You do not have permission to delete this order."}, status=status.HTTP_403_FORBIDDEN)

    order.delete()
    return Response({"detail": "Order deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    user = request.user
    data = request.data
    
    YOUR_DOMAIN = get_current_host(request)

    # Validate that order_items are provided
    order_items = data.get('order_items', [])
    if not order_items:
        return Response({"detail": "No order items provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Prepare shipping details
    shipping_details = {
        'street': data.get('street', ''),
        'city': data.get('city', ''),
        'state': data.get('state', ''),
        'zip_code': data.get('zip_code', ''),
        'country': data.get('country', ''),
        'phone_number': data.get('phone_number', ''),
        'user': user.id # Store user ID for reference
    }

    # Add order items to line items for Stripe
    line_items = []
    for order_item in order_items:
        try:
            product = Product.objects.get(id=order_item['product'])
        except Product.DoesNotExist:
            return Response({"detail": f"Product with id {order_item['product']} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Get all image URLs for the product
        image_urls = [img.image.url for img in product.images.all()]
        # Use the first image for Stripe (Stripe expects a list, but usually only one image is shown)
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': product.name,
                    'images': image_urls[:1],  # Stripe expects a list, so pass the first image if available
                    'metadata': {
                        'product_id': product.id,
                        'user_id': user.id,
                    }
                },
                'unit_amount': int(product.price * 100),  # Convert to cents
            },
            'quantity': order_item.get('quantity', 1),
        })

    # Create the checkout session
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            metadata=shipping_details,
            line_items=line_items,
            customer_email=user.email,
            mode='payment',
            success_url=YOUR_DOMAIN,
            cancel_url=YOUR_DOMAIN,
        )
        return Response({'checkout_session': checkout_session}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Orders which are purhcased through stripe will be handled by webhook
# This will be called by stripe when payment is successful
# Orders from other payment methods will be handled by create_order manually
@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        logger.info("Stripe webhook event constructed successfully.")
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return Response({"detail": "Invalid payload."}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return Response({"detail": "Invalid signature."}, status=status.HTTP_400_BAD_REQUEST)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        logger.info(f"Processing checkout.session.completed for session {session['id']}")

        try:
            line_items = stripe.checkout.Session.list_line_items(session['id'])
            total_amount = session['amount_total'] / 100
            logger.info(f"Total amount from Stripe session: {total_amount}")
        except Exception as e:
            logger.error(f"Error retrieving line items or total amount: {e}")
            return Response({"detail": f"Error retrieving line items: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            user = User.objects.get(id=session['metadata']['user'])
            logger.info(f"User found: {user.username} (ID: {user.id})")
        except User.DoesNotExist:
            logger.error(f"User with id {session['metadata']['user']} not found.")
            return Response({"detail": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Check stock for all products first
        out_of_stock = False
        for item in line_items['data']:
            try:
                stripe_product = stripe.Product.retrieve(item['price']['product'])
                product_id = stripe_product.metadata.get('product_id')
                if not product_id:
                    logger.warning(f"No product_id in Stripe product metadata for item {item['id']}")
                    continue
                product = Product.objects.get(id=product_id)
                if product.stock < item['quantity']:
                    logger.warning(f"Insufficient stock for product '{product.name}' (ID: {product.id}). Requested: {item['quantity']}, Available: {product.stock}")
                    out_of_stock = True
            except Product.DoesNotExist:
                logger.error(f"Product with id {product_id} not found.")
                out_of_stock = True
                continue
            except Exception as e:
                logger.error(f"Error checking stock for product {product_id}: {e}")
                out_of_stock = True
                continue
        
        # If any product is out of stock, set payment_status to REFUNDED and order_status to CANCELED
        if out_of_stock:
            payment_status = PaymentStatus.REFUNDED 
            order_status = OrderStatus.CANCELED
            logger.warning("Order cannot be processed due to insufficient stock. Setting payment_status to REFUNDED and order_status to CANCELED.")
        else:
            payment_status = PaymentStatus.PAID
            order_status = OrderStatus.SHIPPED

        try:
            order = Order.objects.create(
                user=user,
                street=session['metadata']['street'],
                city=session['metadata']['city'],
                state=session['metadata']['state'],
                zip_code=session['metadata']['zip_code'],
                phone_number=session['metadata']['phone_number'],
                country=session['metadata']['country'],
                total_amount=total_amount,
                payment_method=PaymentMethod.CREDIT_CARD,
                order_status=order_status,
                payment_status=payment_status
            )
            logger.info(f"Order {order.id} created with payment_status: {payment_status}")
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return Response({"detail": f"Error creating order: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create order items based on line items
        for item in line_items['data']:
            try:
                stripe_product = stripe.Product.retrieve(item['price']['product'])
                product_id = stripe_product.metadata.get('product_id')
                if not product_id:
                    logger.warning(f"No product_id in Stripe product metadata for item {item['id']}")
                    continue
                product = Product.objects.get(id=product_id)
                image_url = stripe_product['images'][0] if stripe_product['images'] else None
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    name=product.name,
                    quantity=item['quantity'],
                    price=item['price']['unit_amount'] / 100, # Convert back to dollars
                    image=image_url
                )
                logger.info(f"OrderItem created for product '{product.name}' (ID: {product.id}), quantity: {order_item.quantity}")

                # Only reduce stock if enough is available
                if product.stock >= order_item.quantity:
                    product.stock -= order_item.quantity
                    product.save()
                    logger.info(f"Stock updated for product '{product.name}' (ID: {product.id}). New stock: {product.stock}")
                else:
                    logger.warning(f"Stock not reduced for '{product.name}' (ID: {product.id}) due to insufficient stock.")
            except Product.DoesNotExist:
                logger.error(f"Product with id {product_id} not found while creating order item.")
                continue
            except Exception as e:
                logger.error(f"Error creating order item for product {product_id}: {e}")
                continue

        # Log the order id after successful creation
        logger.info(f"Order processing completed successfully. Order ID: {order.id}")
        return Response({'details': 'Payment processed.'}, status=status.HTTP_200_OK)
    
    else:
        # Handle other event types if needed
        logger.warning(f"Unhandled Stripe event type received: {event['type']}")
        return Response({'details': f"Unhandled event type: {event['type']}"}, status=status.HTTP_200_OK)
    
    
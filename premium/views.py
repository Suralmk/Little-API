# views.py
import stripe
from django.conf import settings
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.http import JsonResponse, HttpResponse
from smddapp.models import User
stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
def create_checkout_session(request):
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Little Premium Plan',
                        },
                        'unit_amount': 500,
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://localhost:3000/payment-success',
            cancel_url='http://localhost:3000/payment-cancel',
        )
        return Response({'id': checkout_session.id})
    except Exception as e:
        return Response({'error': str(e)}, status=400)
    

@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = 'your-webhook-signing-secret'

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)
        handle_checkout_session(session)

    # Return a response to acknowledge receipt of the event
    return HttpResponse(status=200)

def handle_checkout_session(session):
    # Handle the successful payment here
    email = session.get("customer_email")  # Use 'customer_email' to retrieve email
    user = User.objects.filter(email=email).first()
    
    if user:
        user.premium = True
        user.save()
        return True
    else:
        return False

import stripe
from django.conf import settings
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.http import JsonResponse
from smddapp.models import User

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
def create_checkout_session(request):
    email = request.data["email"]
    print(email)
    
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
            customer_email=email,
            success_url='http://localhost:3000',
            cancel_url='http://localhost:3000/payment-cancel',
        )
        return Response({'id': checkout_session.id})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@csrf_exempt
@api_view(['POST'])
def stripe_webhook(request):
    payload = request.data
    print(payload)

    try:
         event = stripe.Event.construct_from(
      payload, stripe.api_key
    )
    except ValueError as e:
        print(f"Invalid payload: {e}")
        return JsonResponse(status=400, data={"error" : "Error Upgrading to premium"})
    except stripe.error.SignatureVerificationError as e:
        print(f"Invalid signature: {e}")
        return JsonResponse(status=400, data={"error" : "Error Upgrading to premium"})

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object'] 
        upgraded = handle_checkout_session(session)

        if not upgraded:
            return JsonResponse(status=400, data={"error" : "Error Upgrading to premium"})
        
        return JsonResponse(status=200, data={"error" : "Payment succesful"})
            
def handle_checkout_session(session):
    email = session.get('customer_email') 
    user = User.objects.filter(email=email).first()

    if user:
        user.premium = True
        user.save()
        print(f"User {user.username} has been upgraded to premium.")
        return True
    else:
        print(f"No user found with email {email}.")
        return False
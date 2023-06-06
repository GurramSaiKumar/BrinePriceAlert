from django.shortcuts import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from BTC.serializers import PriceAlertSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from BTC.models import PriceAlert
from rest_framework import status
from django.core.paginator import Paginator
from BTC.utilts import fetch_latest_price, send_email, print_alert_notification, send_email_task
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page


# Create your views here.

def test(request):
    print("Hii I am alive")
    html = "<html><body>Just to test!!</body></html>"
    return HttpResponse(html)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)
            return Response({'token': token}, status=200)
        else:
            return Response({'error': 'Invalid credentials'}, status=401)


class CreateAlertView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request):
        serializer = PriceAlertSerializer(data=request.data)
        if serializer.is_valid():
            alert = serializer.save(user=request.user)
            latest_price = fetch_latest_price(alert.cryptocurrency)

            # Compare the latest price with the target price
            if latest_price is not None and latest_price >= alert.target_price:
                if 'email' in request.data:
                    recipient = request.user.email
                    subject = "Price Alert Triggered"
                    body = f"Congratulations! The price of {alert.cryptocurrency} has reached your target price of " \
                           f"{alert.target_price}."
                    # send_email(recipient, subject, body) #using SMTP
                    send_email_task.delay(recipient, subject, body)  # using celery
                else:
                    print_alert_notification(alert)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class DeleteAlertView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        alert_id = request.data.get('alert_id')

        # Check if the alert exists
        try:
            alert = PriceAlert.objects.get(id=alert_id)
        except PriceAlert.DoesNotExist:
            return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the authenticated user owns the alert
        if alert.user != request.user:
            return Response({'error': 'You do not have permission to delete this alert'},
                            status=status.HTTP_403_FORBIDDEN)
        alert.delete()

        return Response({'success': 'Alert deleted'}, status=status.HTTP_200_OK)


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class AlertsListView(APIView):
    permission_classes = [IsAuthenticated]

    @cache_page(CACHE_TTL)
    def get(self, request):
        cache_key = f'alerts_list_cache_key:{request.user.id}:{hash(frozenset(request.query_params.items()))}'
        # Check if response is already cached
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)

        alerts = PriceAlert.objects.filter(user=request.user)
        status = request.query_params.get('status', None)
        if status:
            alerts = alerts.filter(status=status)

        # Paginate the alerts
        paginator = Paginator(alerts, 10)  # Set the number of alerts per page
        page_number = request.query_params.get('page', 1)
        page_alerts = paginator.get_page(page_number)

        # Serialize the alerts
        serializer = PriceAlertSerializer(page_alerts, many=True)

        # Prepare the response data
        response_data = {
            'count': alerts.count(),
            'next': page_alerts.next_page_number() if page_alerts.has_next() else None,
            'previous': page_alerts.previous_page_number() if page_alerts.has_previous() else None,
            'results': serializer.data
        }
        # Cache the response
        cache.set(cache_key, response_data, CACHE_TTL)
        return Response(response_data)

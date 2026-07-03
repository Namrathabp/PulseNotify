import random
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Count, Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .models import PriceAlert, NotificationLog, UserProfile
from .permissions import IsAdminUser

# --- AUTH ENDPOINTS ---

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        refresh = RefreshToken.for_user(user)

        return Response({
            "username": user.username,
            "access": str(refresh.access_token),
            "role": user.profile.role
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token)
        }, status=status.HTTP_200_OK)


# --- PRICE ALERT ENDPOINTS ---

class PriceAlertListCreateView(APIView):
    def get(self, request):
        alerts = PriceAlert.objects.filter(user=request.user)
        data = [{
            "id": alert.id,
            "origin": alert.origin,
            "destination": alert.destination,
            "threshold_price": str(alert.threshold_price),
            "status": alert.status,
            "created_at": alert.created_at
        } for alert in alerts]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        origin = request.data.get('origin')
        destination = request.data.get('destination')
        threshold_price = request.data.get('threshold_price')

        if not all([origin, destination, threshold_price]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        alert = PriceAlert.objects.create(
            user=request.user,
            origin=origin,
            destination=destination,
            threshold_price=threshold_price
        )
        return Response({
            "id": alert.id,
            "status": alert.status
        }, status=status.HTTP_201_CREATED)


class PriceAlertDeleteView(APIView):
    def delete(self, request, id):
        alert = get_object_or_404(PriceAlert, id=id)
        if alert.user != request.user:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        alert.status = PriceAlert.Status.INACTIVE
        alert.save()
        return Response({"status": "inactive"}, status=status.HTTP_200_OK)


# --- INTERNAL MOCK FEED ---

MOCK_PRICES = {
    'DEL-BOM': (3000, 7000),
    'BLR-HYD': (1500, 4000),
    'DEL-BLR': (4000, 9000),
    'BOM-GOA': (2000, 5000),
}

def get_flight_price(request):
    route = request.GET.get('route', '')
    price_range = MOCK_PRICES.get(route)
    if not price_range:
        return JsonResponse({'error': 'Route not found'}, status=404)
    price = random.randint(*price_range)
    return JsonResponse({'route': route, 'price': price})


# --- ADMIN ENDPOINT ---

class AdminSummaryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Database optimization aggregates
        counts = PriceAlert.objects.aggregate(
            total_alerts=Count('id'),
            active_alerts=Count('id', filter=Q(status=PriceAlert.Status.ACTIVE)),
            triggered_alerts=Count('id', filter=Q(status=PriceAlert.Status.TRIGGERED))
        )
        
        total_notifications = NotificationLog.objects.count()

        # Grouping and aggregating top routes completely inside the engine
        top_routes_qs = PriceAlert.objects.values('origin', 'destination').annotate(
            alert_count=Count('id')
        ).order_by('-alert_count')[:5]

        top_routes = [
            {
                "route": f"{item['origin']}-{item['destination']}",
                "alert_count": item['alert_count']
            } for item in top_routes_qs
        ]

        return Response({
            "total_alerts": counts['total_alerts'] or 0,
            "active_alerts": counts['active_alerts'] or 0,
            "triggered_alerts": counts['triggered_alerts'] or 0,
            "total_notifications": total_notifications,
            "top_routes": top_routes
        }, status=status.HTTP_200_OK)

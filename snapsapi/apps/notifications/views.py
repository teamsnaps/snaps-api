# notifications/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import FCMDevice


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_device(request):
    """디바이스 토큰 등록/갱신 API"""
    registration_id = request.data.get('registration_id')
    device_type = request.data.get('type', 'web')

    if not registration_id:
        return Response({'error': 'registration_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    device, created = FCMDevice.objects.update_or_create(
        user=request.user,
        registration_id=registration_id,
        defaults={
            'type': device_type,
            'active': True
        }
    )

    return Response({
        'id': device.id,
        'registered': created,
        'active': device.active
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

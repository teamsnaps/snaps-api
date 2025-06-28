from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def home(request):
    """
    루트 경로에서 단순 텍스트 메시지를 JSON 형태로 반환
    """
    return Response({
        "message": "Snaps API is running!"
    })


@api_view(['GET'])
def health_check(request):
    """
    /core/health/ 헬스체크 엔드포인트
    status: ok JSON 반환
    """
    return Response({
        "status": "ok"
    })

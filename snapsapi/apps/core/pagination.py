from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardResultsSetPagination(PageNumberPagination):
    """
    프로젝트 전반에 걸쳐 사용할 표준 페이지네이션 클래스입니다.
    - `page_size`: 한 페이지에 보여줄 항목 수
    - `page_size_query_param`: 클라이언트가 페이지 당 항목 수를 직접 지정할 때 사용하는 쿼리 파라미터
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        API 응답 형식을 커스터마이징합니다.
        """
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
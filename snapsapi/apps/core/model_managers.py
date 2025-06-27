from typing import TYPE_CHECKING

from django.db import models

from snapsapi.apps.core.exceptions import FollowYourselfException

if TYPE_CHECKING:
    from snapsapi.apps.users.models import User
    from snapsapi.apps.core.models import Follow


class FollowManager(models.Manager):
    def follow(self, follower: 'User', following: 'User') -> tuple['Follow', bool]:
        """
        'follower'가 'following'을 팔로우하는 관계를 생성합니다.
        이미 존재하는 관계라면 아무것도 하지 않고 기존 객체를 반환합니다.

        :param follower: 팔로우를 요청하는 사용자
        :param following: 팔로우 대상이 되는 사용자
        :return: (Follow 객체, 생성 여부(created) boolean) 튜플
        """
        if follower == following:
            raise FollowYourselfException()

        # get_or_create를 사용하면 이미 객체가 존재할 경우 그것을 가져오고,
        # 없을 경우 새로 생성하므로 중복 생성을 막을 수 있습니다.
        obj, created = self.get_or_create(follower=follower, following=following)
        return obj, created

    def unfollow(self, follower: 'User', following: 'User') -> int:
        """
        'follower'가 'following'을 팔로우하는 관계를 삭제합니다.

        :param follower: 언팔로우를 요청하는 사용자
        :param following: 언팔로우 대상이 되는 사용자
        :return: 삭제된 객체의 수 (0 또는 1)
        """
        # filter().delete()는 대상이 없어도 오류를 발생시키지 않고 0을 반환합니다.
        deleted_count, _ = self.filter(follower=follower, following=following).delete()
        return deleted_count

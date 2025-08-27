from typing import Optional, Dict
from snapsapi.apps.notifications.services.fcm import FCMService


class NotificationService:
    def __init__(self, fcm: Optional[FCMService] = None):
        self.fcm = fcm or FCMService()

    def send_comment_created(
            self,
            to_user_id: int,
            actor_username: str,
            post_id: str,
            comment_id: str,
            preview: Optional[str] = None,
    ) -> Optional[str]:
        title = "새 댓글 알림"
        body = (f"{actor_username}님: {preview}" if preview
                else f"{actor_username}님이 회원님의 게시물에 댓글을 남겼습니다.",)
        data: Dict[str, str] = {
            "type": "new_comment",
            "post_id": str(post_id),
            "comment_id": str(comment_id),
        }
        return self.fcm.send_notifications_to_user(
            user_id=to_user_id,
            title=title,
            body=body,
            data=data,
        )

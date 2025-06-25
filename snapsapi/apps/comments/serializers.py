from rest_framework import serializers
from snapsapi.apps.posts.models import Post
from snapsapi.apps.comments.models import Comment
from snapsapi.apps.users.serializers import UserLoginSerializer

from rest_framework import serializers

from snapsapi.apps.comments.models import Comment
from snapsapi.apps.posts.models import Post


class CommentReadSerializer(serializers.ModelSerializer):
    """
    댓글 조회(GET)를 위한 Serializer입니다.
    작성자 정보와 대댓글(replies)을 포함합니다.
    """
    user = UserLoginSerializer(read_only=True)   # Todo: modified serializer
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'uid',
            'user',
            'content',
            'created_at',
            'parent',
            'replies',
        ]
        read_only_fields = fields

    def get_replies(self, instance):
        """
        재귀적으로 대댓글을 직렬화합니다.
        """
        if instance.replies.exists():
            return CommentReadSerializer(instance.replies.all(), many=True, context=self.context).data
        return []


class CommentCreateSerializer(serializers.Serializer):
    """
    댓글 생성(POST)을 위한 Serializer입니다.
    View로부터 post 객체를 받아 댓글을 생성합니다.
    """
    # 1. post_uid 필드를 제거합니다. URL에서 정보를 얻기 때문입니다.
    content = serializers.CharField(max_length=255, help_text="댓글 내용")
    parent_uid = serializers.UUIDField(required=False, allow_null=True, write_only=True, help_text="대댓글인 경우 부모 댓글의 UID")

    def validate(self, data):
        """
        데이터 유효성 검증:
        - 부모 댓글이 있다면, URL로 들어온 게시물에 속한 댓글인지 확인합니다.
        """
        parent_uid = data.get('parent_uid')
        post = self.context.get('post')  # View에서 전달해준 post 객체

        if parent_uid:
            try:
                # 부모 댓글이면서, 현재 post에 속한 댓글인지 함께 확인합니다.
                parent_comment = Comment.objects.get(uid=parent_uid, post=post)
                data['parent'] = parent_comment  # create 메서드에서 사용할 수 있도록 객체를 data에 추가
            except Comment.DoesNotExist:
                raise serializers.ValidationError({'parent_uid': '부모 댓글을 찾을 수 없거나 다른 게시물의 댓글입니다.'})
        else:
            data['parent'] = None

        return data

    def create(self, validated_data):
        """
        유효성 검증을 통과한 데이터로 Comment 객체를 생성합니다.
        """
        user = self.context['request'].user
        post = self.context['post']  # View가 context에 담아준 post 객체를 사용
        content = validated_data.get('content')
        parent = validated_data.get('parent')  # validate 메서드에서 추가해준 parent 객체

        comment = Comment.objects.create_comment(
            user=user,
            post=post,
            content=content,
            parent=parent
        )
        return comment

    def to_representation(self, instance):
        """
        생성된 객체를 API 응답 형식으로 변환합니다.
        """
        return CommentReadSerializer(instance, context=self.context).data


class CommentUpdateSerializer(serializers.ModelSerializer):
    """
    댓글 수정(PATCH)을 위한 Serializer입니다.
    'content' 필드만 수정 가능하도록 제한합니다.
    """
    class Meta:
        model = Comment
        fields = ['content']
        # content 필드에 추가적인 제약사항을 설정할 수 있습니다.
        extra_kwargs = {
            'content': {
                'required': True,  # content 필드는 수정 시 필수 항목입니다.
                'allow_blank': False  # 빈 문자열을 허용하지 않습니다.
            }
        }

    def update(self, instance, validated_data):
        """
        댓글의 content를 업데이트합니다.
        ModelSerializer의 기본 update 동작을 사용합니다.
        """
        # 소유권 검증은 View에서 처리하는 것이 일반적입니다.
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance

    def to_representation(self, instance):
        """
        수정된 객체를 API 응답 형식으로 변환합니다.
        읽기용 Serializer를 사용하여 일관된 응답을 제공합니다.
        """
        return CommentReadSerializer(instance, context=self.context).data

class CommentDeleteSerializer:
    pass
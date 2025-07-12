# 기존 사용자 목록 가져오기
import os
import django
# Django 설정 모듈 지정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'snapsapi.settings.prod')  # 실제 설정 경로로 수정

# Django 초기화
django.setup()

from datetime import timezone, timedelta
import random
from datetime import datetime, UTC
from django.contrib.auth import get_user_model
from django.db import transaction

from snapsapi.apps.posts.models import Post, PostImage, Tag



def generate_random_text(min_length=50, max_length=200):
    # 영어 문장에 사용할 단어 목록
    words = [
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "I",
        "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
        "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
        "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
        "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
        "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
        "people", "into", "year", "your", "good", "some", "could", "them", "see", "other",
        "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
        "back", "after", "use", "two", "how", "our", "work", "first", "well", "way",
        "even", "new", "want", "because", "any", "these", "give", "day", "most", "us",
        "post", "image", "photo", "awesome", "amazing", "beautiful", "cool", "nice", "great", "love",
        "happy", "fun", "friend", "family", "travel", "food", "music", "art", "nature", "life"
    ]

    # 마침표, 쉼표, 느낌표, 물음표 등의 문장 부호
    punctuation = [".", ".", ".", "!", "?", ",", ";", ":"]

    # 랜덤 길이 결정
    length = random.randint(min_length, max_length)

    # 단어 개수 결정 (평균 5글자 단어 + 공백 가정)
    word_count = length // 6

    # 텍스트 생성
    text = []
    for i in range(word_count):
        word = random.choice(words)

        # 문장 시작 시 대문자로
        if i == 0 or text[-1][-1] in [".", "!", "?"]:
            word = word.capitalize()

        # 약 10%의 확률로 문장 부호 추가
        if random.random() < 0.1 and i < word_count - 1:
            word += random.choice(punctuation)

        text.append(word)

    # 마지막 단어에 마침표 추가
    if text[-1][-1] not in [".", "!", "?"]:
        text[-1] += "."

    # 공백으로 합치기
    return " ".join(text)


User = get_user_model()
users = list(User.objects.all()[:10])  # 최대 10명의 사용자 가져오기

tag_names = ['여행', '음식', '패션', '일상', '스포츠', '영화', '음악', '예술', '취미', '반려동물']
for tag_name in tag_names:
    if not Tag.objects.filter(name=tag_name).exists():
        Tag.objects.create(name=tag_name)
existing_tags = list(Tag.objects.all()[:20])

sample_image_urls = [
    'media/posts/test/520-360x270.jpg',
    'media/posts/test/14-360x270.jpg',
    'media/posts/test/19-360x270.jpg',
    'media/posts/test/34-360x270.jpg',
    'media/posts/test/149-360x270.jpg',
    'media/posts/test/153-360x270.jpg',
    'media/posts/test/155-360x270.jpg',
    'media/posts/test/171-360x270.jpg',
    'media/posts/test/198-360x270.jpg',
    'media/posts/test/254-360x270.jpg',
    'media/posts/test/301-360x270.jpg',
    'media/posts/test/379-360x270.jpg',
    'media/posts/test/464-360x270.jpg',
    'media/posts/test/570-360x270.jpg',
    'media/posts/test/654-360x270.jpg',
    'media/posts/test/659-360x270.jpg',
    'media/posts/test/835-360x270.jpg',
    'media/posts/test/903-360x270.jpg',
    'media/posts/test/958-360x270.jpg',
    'media/posts/test/992-360x270.jpg'
]


def create_posts(count=1000, batch_size=100):
    total_created = 0

    print(f"{count}개의 게시물 생성을 시작합니다...")

    # 배치 처리로 성능 최적화
    for i in range(0, count, batch_size):
        batch_count = min(batch_size, count - i)

        with transaction.atomic():  # 트랜잭션으로 묶어 DB 작업 최적화
            for j in range(batch_count):
                current = i + j + 1

                # 랜덤 사용자 선택
                user = random.choice(users)

                # 게시물 생성 시간 (최근 30일 내에서 랜덤)
                created_at = datetime.now(UTC) - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )

                # 영어로 랜덤 캡션 생성
                caption = generate_random_text(50, 200)

                image_count = random.randint(1, 5)
                images = [random.choice(sample_image_urls) for k in range(image_count)]

                tag_count = random.randint(0, 5)
                selected_tags = random.sample(existing_tags, min(tag_count, len(existing_tags)))
                tags = [tag.name for tag in selected_tags]
                Post.objects.create_post(user=user,
                                         caption=caption,
                                         images=images,
                                         tags=tags,
                                         created_at=created_at,
                                         updated_at=created_at)

                # 진행 상황 표시 (10%마다)
                if current % (count // 10) == 0 or current == count:
                    progress = (current / count) * 100
                    print(f"진행 중... {progress:.1f}% ({current}/{count})")

        total_created += batch_count

    print(f"게시물 생성 완료! 총 {total_created}개의 게시물이 생성되었습니다.")
    return total_created


create_posts()

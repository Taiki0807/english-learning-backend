from datetime import datetime

import shortuuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class Course(models.Model):
    id = models.CharField(max_length=22, default=shortuuid.uuid, primary_key=True)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class CourseAccessHistory(models.Model):
    id = models.CharField(max_length=22, default=shortuuid.uuid, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    accessed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-accessed_at"]  # 最新のアクセスが上に来るように降順で並べます


class CourseProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    current_index = models.PositiveIntegerField(default=0)  # 現在のインデックス

    class Meta:
        unique_together = ["user", "course"]


class FlashcardManager(models.Manager):
    def get_next_flashcards(self, user, course, count):
        now = timezone.localtime(timezone.now())
        flashcards = self.filter(user=user, course=course, next_review_date__lte=now).order_by("next_review_date")[
            :count
        ]
        return flashcards


class Flashcard(models.Model):
    id = models.CharField(max_length=22, default=shortuuid.uuid, primary_key=True)
    word = models.CharField(max_length=100)
    meaning = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="flashcards")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_review_date = models.DateTimeField(null=True, blank=True)
    next_review_date = models.DateTimeField(null=True, blank=True)
    total_reviews = models.PositiveIntegerField(default=0)  # 総レビュー回数
    correct_reviews = models.PositiveIntegerField(default=0)  # 正答したレビュー回数
    objects = FlashcardManager()

    def __str__(self):
        return self.word

    def calculate_next_review_date(self, correct):
        # 忘却曲線の計算を行う
        if correct:
            # 正答した場合、次のレビュー日時を1日後に設定
            self.next_review_date = self.last_review_date + datetime.timedelta(days=1)
            self.correct_reviews += 1
        else:
            # 不正答だった場合、次のレビュー日時を3日後に設定
            self.next_review_date = self.last_review_date + datetime.timedelta(days=3)
        self.total_reviews += 1
        self.save()

    @staticmethod
    def get_next_flashcards(user, count):
        now = timezone.now()
        flashcards = Flashcard.objects.filter(user=user, next_review_date__lte=now).order_by("next_review_date")[
            :count
        ]
        return flashcards


class Review(models.Model):
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    correct = models.BooleanField()
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.flashcard.word}"


class UserLearningData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    correct_answers = models.PositiveIntegerField(default=0)
    total_answers = models.PositiveIntegerField(default=0)
    round_count = models.PositiveIntegerField(default=0)  # 単語帳の周回数
    review_dates = models.JSONField(default=list)
    retention_rates = models.JSONField(default=list)

    def add_review_data(self, review_date=None, retention_rate=None):
        if review_date is not None:
            self.forgetting_curve["review_date"].append(review_date)
        if retention_rate is not None:
            self.forgetting_curve["retention_rate"].append(retention_rate)
        self.save()


class RetentionRate(models.Model):
    review_date = models.DateTimeField(default=datetime.now)
    retention_rate = models.FloatField()


class QuizQuestion(models.Model):
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

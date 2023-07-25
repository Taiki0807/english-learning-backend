from datetime import datetime

from rest_framework import serializers

from .models import Course, CourseAccessHistory, CourseProgress, Flashcard, QuizQuestion, Review, UserLearningData


class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = ["id", "word", "meaning", "user", "last_review_date", "next_review_date", "course_id"]

    def create(self, validated_data):
        request_data = self.context["request"].data
        course_id = request_data[0].get("course_id")
        validated_data["course_id"] = course_id
        validated_data["last_review_date"] = datetime.now()
        validated_data["next_review_date"] = datetime.now()
        return super().create(validated_data)


class CourseSerializer(serializers.ModelSerializer):
    words = FlashcardSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "name", "words", "user"]


class CourseAccessHistorySerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = CourseAccessHistory
        fields = ("id", "user", "course", "accessed_at")


class CourseProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseProgress
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"


class ResetFlashcardStatsRequestSerializer(serializers.Serializer):
    course_id = serializers.CharField()


class UserLearningDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLearningData
        fields = ["correct_answers", "total_answers", "round_count", "review_dates", "retention_rates"]


class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = "__all__"

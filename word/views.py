from datetime import datetime

from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, CourseAccessHistory, CourseProgress, Flashcard, Review, UserLearningData
from .serializers import (
    CourseAccessHistorySerializer,
    CourseProgressSerializer,
    CourseSerializer,
    FlashcardSerializer,
    ResetFlashcardStatsRequestSerializer,
    ReviewSerializer,
    UserLearningDataSerializer,
)


class FlashcardListCreateView(generics.ListCreateAPIView):
    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # バリデーションを通過したオブジェクトを保存し、インスタンスのリストを取得
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class FlashcardRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer


@receiver(post_save, sender=Review)
def update_user_learning_data(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        course = instance.flashcard.course
        learning_data, _ = UserLearningData.objects.get_or_create(user=user, course=course)
        learning_data.total_answers += 1
        if instance.correct:
            learning_data.correct_answers += 1
        learning_data.save()


class ReviewListView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Review.objects.filter(user=user)

        course_id = self.request.query_params.get("course_id")
        if course_id:
            queryset = queryset.filter(flashcard__course_id=course_id)

        review_date = self.request.query_params.get("review_date")
        if review_date:
            try:
                review_date = datetime.strptime(review_date, "%Y-%m-%d")
                queryset = queryset.filter(review_date__date=review_date.date())
            except ValueError:
                queryset = Review.objects.none()

        return queryset

    def get_course_data(self, course):
        self.get_queryset()

        queryset_course = Review.objects.filter(flashcard__course=course)
        flashcards_count = course.flashcards.count()

        correct_reviews_count = queryset_course.filter(correct=True).count()

        # UserLearningDataをシリアライズ
        user_learning_data = UserLearningData.objects.filter(user=self.request.user, course=course).first()
        user_learning_data_serializer = UserLearningDataSerializer(user_learning_data)

        course_data = {
            "reviews": ReviewSerializer(queryset_course, many=True).data,
            "course_learning_rate": correct_reviews_count / len(queryset_course) if len(queryset_course) > 0 else 0.0,
            "course_progress_rate": correct_reviews_count / flashcards_count if flashcards_count > 0 else 0.0,
            "user_learning_data": user_learning_data_serializer.data,
        }

        return course_data

    def get_course_progress_rate(self, course):
        queryset_course = Review.objects.filter(flashcard__course=course)
        flashcards_count = course.flashcards.count()
        correct_reviews_count = queryset_course.filter(correct=True).count()

        course_progress_rate = correct_reviews_count / flashcards_count if flashcards_count > 0 else 0.0
        return course_progress_rate

    def perform_create(self, serializer):
        flashcard = serializer.validated_data.get("flashcard")
        user = self.request.user

        # 既存のレビューを取得
        existing_review = Review.objects.filter(flashcard=flashcard, user=user).first()
        # レビューの保存後に関連データを更新する
        course = flashcard.course
        course_progress_rate = self.get_course_progress_rate(course)
        # UserLearningDataを取得または作成
        user_learning_data, _ = UserLearningData.objects.get_or_create(user=user, course=course)

        # 正解の場合はcorrect_answersを加算
        if serializer.validated_data.get("correct"):
            user_learning_data.correct_answers = F("correct_answers") + 1
        user_learning_data.total_answers = F("total_answers") + 1
        user_learning_data.save()
        # CourseProgressを取得または作成してcurrent_indexを更新
        course_progress, _ = CourseProgress.objects.get_or_create(user=user, course=course)
        course_progress.current_index = F("current_index") + 1
        course_progress.save()

        # データベースから最新の値を取得
        user_learning_data.refresh_from_db()
        if len(user_learning_data.review_dates) == 0 and user_learning_data.total_answers == 1:
            user_learning_data.review_dates.append(str(datetime.now()))
        user_learning_data.save()

        if existing_review:
            if serializer.validated_data.get("correct"):
                user_learning_data.refresh_from_db()
                print("hhello ok")
                print(user_learning_data.correct_answers)
                print(course.flashcards.count())

                if course_progress_rate == 1 and user_learning_data.correct_answers == course.flashcards.count():
                    print("ok")
                    user_learning_data.round_count += 1
                    user_learning_data.review_dates.append(str(datetime.now()))
                    if len(user_learning_data.review_dates) % 3 == 0:
                        last_index = len(user_learning_data.review_dates) - 1
                        date_1 = datetime.strptime(user_learning_data.review_dates[last_index], "%Y-%m-%d %H:%M:%S.%f")
                        date_2 = datetime.strptime(
                            user_learning_data.review_dates[last_index - 1], "%Y-%m-%d %H:%M:%S.%f"
                        )
                        date_3 = datetime.strptime(
                            user_learning_data.review_dates[last_index - 2], "%Y-%m-%d %H:%M:%S.%f"
                        )
                        timedelta_1 = date_1 - date_2
                        timedelta_2 = date_2 - date_3
                        print("time1 %f", timedelta_1)
                        print("time2 %f", timedelta_2)
                        ratio = timedelta_1 / timedelta_2
                        savings_rate = min(ratio, 1.0)
                        user_learning_data.retention_rates.append(savings_rate)
                    user_learning_data.save()

            # 既存のレビューがある場合は上書きする
            serializer.update(existing_review, serializer.validated_data)
            existing_review.review_date = datetime.now()  # レビュー日時を現在の日時に更新する
            existing_review.save()

        else:
            review = serializer.save(user=user, flashcard=flashcard)
            # 初回のレビューの場合のみ、経過時間を計算する
            if user_learning_data.round_count == 0:
                user_learning_data.round_count = 1
                user_learning_data.review_dates.append(str(datetime.now()))
                review.review_date = datetime.now()  # レビュー日時を現在の日時に設定する
                review.save()

        data = self.get_course_data(course)
        return Response(data)

    def list(self, request, *args, **kwargs):
        course_id = self.request.query_params.get("course_id")

        if course_id:
            course = get_object_or_404(Course, id=course_id)
            data = {course_id: [self.get_course_data(course)]}
        else:
            courses = Course.objects.all()
            data = {}

            for course in courses:
                data[course.id] = [self.get_course_data(course)]

        return Response(data)


class ResetFlashcardStatsAPIView(APIView):
    @extend_schema(
        request=ResetFlashcardStatsRequestSerializer,
        responses={200: {"message": "Flashcard stats reset successfully."}},
    )
    def post(self, request, *args, **kwargs):
        course_id = request.data.get("course_id")

        # 指定されたコースに関連するUserLearningDataを取得
        user_learning_data_list = UserLearningData.objects.filter(course_id=course_id)

        if user_learning_data_list.exists():
            # UserLearningDataをリセット
            user_learning_data_list.update(correct_answers=0, total_answers=0)
            # CourseProgressを取得してcurrent_indexをリセット
            course_progress_list = CourseProgress.objects.filter(course_id=course_id)
            if course_progress_list.exists():
                # フラッシュカードの総数を取得
                total_flashcards = Flashcard.objects.filter(course_id=course_id).count()

                # current_indexが問題数と同じであればリセット
                course_progress_list = course_progress_list.filter(current_index=total_flashcards)
                if course_progress_list.exists():
                    course_progress_list.update(current_index=0)
            return Response({"message": "Flashcard stats reset successfully."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "No UserLearningData found for the given course."}, status=status.HTTP_404_NOT_FOUND
            )


class ResetLearningProgressUnconditionallyAPIView(APIView):
    @extend_schema(
        request=ResetFlashcardStatsRequestSerializer,
        responses={200: {"message": "Flashcard stats reset successfully."}},
    )
    def post(self, request, *args, **kwargs):
        course_id = request.data.get("course_id")

        # 指定されたコースに関連するUserLearningDataを取得
        user_learning_data_list = UserLearningData.objects.filter(course_id=course_id)

        if user_learning_data_list.exists():
            # UserLearningDataをリセット
            user_learning_data_list.update(correct_answers=0, total_answers=0)
            # CourseProgressを取得してcurrent_indexをリセット
            course_progress_list = CourseProgress.objects.filter(course_id=course_id)
            if course_progress_list.exists():
                # current_indexが問題数と同じであればリセット
                course_progress_list = course_progress_list.update(current_index=0)
            return Response({"message": "Flashcard stats reset successfully."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "No UserLearningData found for the given course."}, status=status.HTTP_404_NOT_FOUND
            )


class UserStatsAndForgettingCurveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        reviews = Review.objects.filter(user=user).order_by("review_date")

        total_reviews = reviews.count()
        correct_reviews = reviews.filter(correct=True).count()
        accuracy = correct_reviews / total_reviews if total_reviews > 0 else 0.0

        # user_learning_data, _ = UserLearningData.objects.get_or_create(user=user)

        # forgetting_curve = user_learning_data.forgetting_curve

        data = {
            "user": user.username,
            "accuracy": accuracy,
        }

        return Response(data)


class FlashcardIdListView(generics.ListCreateAPIView):
    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # オブジェクトを保存
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def bulk_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # バリデーションを通過したオブジェクトを保存し、インスタンスのリストを取得
        return Response(status=status.HTTP_201_CREATED)


class QuizQuestionListView(generics.ListAPIView):
    def get_queryset(self):
        user = self.request.user
        count = int(self.request.query_params.get("count", 5))  # デフォルトの問題数は5
        flashcards = Flashcard.objects.get_next_flashcards(user, count)
        return [flashcard.id for flashcard in flashcards]  # idのリストを返す

    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=401)
        queryset = self.get_queryset()
        return Response(queryset)


class CourseListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseWordListAPIView(APIView):
    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            words = course.flashcards.all()  # コースに関連する単語一覧を取得
            serializer = FlashcardSerializer(words, many=True)
            return Response(serializer.data)
        except Course.DoesNotExist:
            return Response(status=404)


class CourseWordQuizAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            count = int(request.query_params.get("count", 20))  # デフォルトの問題数は5
            page = int(request.query_params.get("page", 1))  # デフォルトのページ番号は1
            if request.user.is_authenticated:
                access_history, created = CourseAccessHistory.objects.get_or_create(
                    user=request.user,
                    course=course,
                )
                # 存在している場合はaccessed_atを更新する
                if not created:
                    access_history.accessed_at = timezone.localtime(timezone.now())
                    access_history.save()
                start_index = (page - 1) * count  # 取得開始位置の計算
                flashcards = Flashcard.objects.get_next_flashcards(request.user, course, count)

                # ページング
                start_index = (page - 1) * count
                flashcards = flashcards[start_index : start_index + count]

                serializer = FlashcardSerializer(flashcards, many=True)
                return Response(serializer.data)
            else:
                return Response({"detail": "Authentication credentials were not provided."}, status=401)
        except Course.DoesNotExist:
            return Response(status=404)


class RecentlyAccessedCoursesAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # ログインしているユーザーの最近アクセスしたコースを取得（上位5件とします）
        queryset = CourseAccessHistory.objects.filter(user=request.user).order_by("-accessed_at")[:5]
        serializer = CourseAccessHistorySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseProgressAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        user = self.request.user
        course = Course.objects.get(id=course_id)

        try:
            course_progress = CourseProgress.objects.get(user=user, course=course)
        except CourseProgress.DoesNotExist:
            # CourseProgressが存在しない場合は新しく作成する
            course_progress = CourseProgress.objects.create(user=user, course=course)

        serializer = CourseProgressSerializer(course_progress)
        return Response(serializer.data, status=status.HTTP_200_OK)

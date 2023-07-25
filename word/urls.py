from django.urls import path

from .views import (
    CourseDetailView,
    CourseListView,
    CourseProgressAPIView,
    CourseWordListAPIView,
    CourseWordQuizAPIView,
    FlashcardIdListView,
    FlashcardListCreateView,
    FlashcardRetrieveUpdateDestroyView,
    QuizQuestionListView,
    RecentlyAccessedCoursesAPIView,
    ResetFlashcardStatsAPIView,
    ResetLearningProgressUnconditionallyAPIView,
    ReviewListView,
    UserStatsAndForgettingCurveView,
)

urlpatterns = [
    path("flashcards/", FlashcardListCreateView.as_view(), name="flashcard-list"),
    path("flashcards/<str:pk>/", FlashcardRetrieveUpdateDestroyView.as_view(), name="flashcard-detail"),
    path("reviews/", ReviewListView.as_view(), name="review"),
    path("end-session/", ResetFlashcardStatsAPIView.as_view(), name="end_session"),
    path("user/stats/", UserStatsAndForgettingCurveView.as_view(), name="user-stats"),
    path("flashcards/ids/", FlashcardIdListView.as_view(), name="flashcard-id-list"),
    path("quiz/questions/", QuizQuestionListView.as_view(), name="quiz-question-create"),
    path("courses/", CourseListView.as_view(), name="course-list"),
    path("courses/<str:pk>/", CourseDetailView.as_view(), name="course-detail"),
    path("courses/<str:course_id>/words/", CourseWordListAPIView.as_view(), name="course_word_list"),
    path("courses/<str:course_id>/quiz/", CourseWordQuizAPIView.as_view(), name="course-word-quiz"),
    path("recently-accessed-courses/", RecentlyAccessedCoursesAPIView.as_view(), name="recently-accessed-courses"),
    path("course-progress/<str:course_id>/", CourseProgressAPIView.as_view(), name="course-progress"),
    path("reset-unconditionally/", ResetLearningProgressUnconditionallyAPIView.as_view(), name="reset"),
]

from django.contrib import admin

from .models import Course, CourseAccessHistory, Flashcard, QuizQuestion, Review

admin.site.register(Course)
admin.site.register(Flashcard)
admin.site.register(Review)
admin.site.register(QuizQuestion)
admin.site.register(CourseAccessHistory)

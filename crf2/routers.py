from rest_framework import routers

from course.viewsets import CourseViewSet

# from article.viewsets import ArticleViewSet


router = routers.DefaultRouter()
router.register("course", CourseViewSet)

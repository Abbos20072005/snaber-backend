from django.urls import path

from apps.review.api.v1.views.comments import (
    CommentDetailUpdateDeleteView,
    CommentListCreateView,
    CommentStatusView,
)

urlpatterns = [
    path("comments/", CommentListCreateView.as_view(), name="comment-list-create"),
    path(
        "comments/<int:id>/",
        CommentDetailUpdateDeleteView.as_view(),
        name="comment-detail-update-delete",
    ),
    path(
        "comment-status/",
        CommentStatusView.as_view(),
        name="comment-status",
    ),
]

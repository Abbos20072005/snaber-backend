from django.db.models import Avg
from rest_framework import status

from apps.core.exceptions import (
    ActionNotAllowedException,
    MissingParamsException,
    ObjectNotFoundException,
    PermissionDeniedException,
)
from apps.core.services import BaseService
from apps.order.models import Order
from apps.product.models import Product
from apps.review.api.v1.serializers.comments import (
    CommentCreateSerializer,
    CommentListSerializer,
    CommentStatusSerializer,
    CommentUpdateSerializer,
)
from apps.review.models import Comment, CommentImage


class CommentService(BaseService):
    def get_product_comments(self, *args, **kwargs):
        product_id = self.request.query_params.get("product")

        comments = Comment.objects.select_related("product", "user")

        if product_id:
            comments = comments.filter(product_id=product_id)

        comments = comments.prefetch_related("images")
        return self.get_paginated_response(
            comments, CommentListSerializer, context={"request": self.request}
        )

    def get_comment(self, *args, **kwargs):
        try:
            comment = (
                Comment.objects.select_related("product", "user")
                .prefetch_related("images")
                .get(id=kwargs.get("id"))
            )
        except Comment.DoesNotExist:
            raise ObjectNotFoundException(message="Comment not found")
        return self.get_response_object(
            comment, CommentListSerializer, context={"request": self.request}
        )

    def get_comment_status(self, *args, **kwargs):
        product_id = self.request.query_params.get("product")
        user = self.request.user

        if not product_id:
            raise MissingParamsException(message="product parameter is required")

        if user.is_anonymous:
            data = {
                "can_comment": False,
                "has_commented": False,
            }
            return self.get_response_object(
                data, CommentStatusSerializer, context={"request": self.request}
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ObjectNotFoundException(message="Product not found")

        has_purchased = Order.objects.filter(
            buyer=user,
            items__product=product,
        ).exists()

        has_commented = Comment.objects.filter(
            user=user,
            product=product,
        ).exists()

        data = {
            "can_comment": has_purchased and not has_commented,
            "has_commented": has_commented,
        }

        return self.get_response_object(
            data, CommentStatusSerializer, context={"request": self.request}
        )

    def create_comment(self, *args, **kwargs):
        serializer = CommentCreateSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)

        user = self.request.user
        product = serializer.validated_data["product"]

        if not Order.objects.filter(
            buyer=user,
            items__product=product,
        ).exists():
            raise ActionNotAllowedException(
                message="You can only comment on products you have purchased"
            )

        comment = Comment.objects.create(
            user=user,
            product=product,
            text=serializer.validated_data["text"],
            rating=serializer.validated_data["rating"],
        )

        for image_file in serializer.validated_data.get("images", []):
            CommentImage.objects.create(comment=comment, image=image_file)

        self._update_ratings(product)

        comment = (
            Comment.objects.select_related("product", "user")
            .prefetch_related("images")
            .get(id=comment.id)
        )
        return self.get_response_object(
            comment,
            CommentListSerializer,
            context={"request": self.request},
            status_code=status.HTTP_201_CREATED,
        )

    def update_comment(self, *args, **kwargs):
        try:
            comment = Comment.objects.get(id=kwargs.get("id"))
        except Comment.DoesNotExist:
            raise ObjectNotFoundException(message="Comment not found")

        if comment.user != self.request.user:
            raise PermissionDeniedException(
                message="You can only update your own comments"
            )

        serializer = CommentUpdateSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)

        if "text" in serializer.validated_data:
            comment.text = serializer.validated_data["text"]

        if "rating" in serializer.validated_data:
            comment.rating = serializer.validated_data["rating"]

        if "images" in serializer.validated_data:
            for image in comment.images.all():
                image.delete()
            for image_file in serializer.validated_data["images"]:
                CommentImage.objects.create(comment=comment, image=image_file)

        comment.save()

        self._update_ratings(comment.product)

        comment = (
            Comment.objects.select_related("product", "user")
            .prefetch_related("images")
            .get(id=comment.id)
        )
        return self.get_response_object(
            comment, CommentListSerializer, context={"request": self.request}
        )

    def delete_comment(self, *args, **kwargs):
        try:
            comment = Comment.objects.select_related("product").get(
                id=kwargs.get("id")
            )
        except Comment.DoesNotExist:
            raise ObjectNotFoundException(message="Comment not found")

        if comment.user != self.request.user:
            raise PermissionDeniedException(
                message="You can only delete your own comments"
            )

        product = comment.product
        comment.delete()
        self._update_ratings(product)

        return self.get_response_object(
            context={"request": self.request},
            status_code=status.HTTP_204_NO_CONTENT,
        )

    @staticmethod
    def _update_ratings(product):
        product_avg = Comment.objects.filter(product=product).aggregate(
            Avg("rating")
        )["rating__avg"]
        Product.objects.filter(id=product.id).update(
            average_rating=round(product_avg, 1) if product_avg else 0.0
        )

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Avg
from .models import Review
from .serializers import ReviewSerializer
from .permissions import IsReviewer
from auth_app.permissions import IsCustomerUser
from auth_app.models import Profile
from offers_app.models import Offer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Review model.

    Customers can create reviews; reviewers can update/delete their own reviews.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewer]
    pagination_class = None

    def get_queryset(self):
        """
        Optionally filter by business_user_id or reviewer_id.
        """
        queryset = self.queryset
        business_user_id = self.request.query_params.get('business_user_id')
        reviewer_id = self.request.query_params.get('reviewer_id')
        ordering = self.request.query_params.get('ordering')

        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)
        if ordering in ['updated_at', 'rating']:
            queryset = queryset.order_by(ordering)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create a review.

        Only customer users can create reviews.
        """
        if not IsCustomerUser().has_permission(request, self):
            return Response(
                {"error": "Only customer users can create reviews."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([AllowAny])
def base_info_view(request):
    """
    Return platform-wide statistics.

    Includes review count, average rating, business profile count, and offer count.
    """
    review_count = Review.objects.count()
    average_rating = Review.objects.aggregate(
        avg_rating=Avg('rating')
    )['avg_rating'] or 0
    average_rating = round(average_rating, 1)

    business_profile_count = Profile.objects.filter(type='business').count()
    offer_count = Offer.objects.count()

    data = {
        "review_count": review_count,
        "average_rating": average_rating,
        "business_profile_count": business_profile_count,
        "offer_count": offer_count,
    }
    return Response(data)
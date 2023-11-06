from django.db.models import Count
from rest_framework import generics, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Profile
from .serializers import ProfileSerializer
from craft_api.permissions import IsOwnerOrReadOnly
from django.contrib.auth import logout as django_logout


class ProfileList(generics.ListAPIView):
    """
    List all profiles
    No post method as profile creation is handled by django signals
    in the models.py create_profile method.
    """
    serializer_class = ProfileSerializer
    queryset = Profile.objects.annotate(
        posts_count=Count('owner__post', distinct=True),
        followers_count=Count('owner__followed', distinct=True),
        following_count=Count('owner__following', distinct=True),
        approval_count=Count('approval__owner', distinct=True),
    ).order_by('-created_on')
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    ordering_fields = [
        'posts_count',
        'followers_count',
        'following_count',
        'approval_count',
        'owner__following__created_on',
        'owner__followed__created_on',
    ]
    search_fields = [
        'owner__username',
        'name',
        'job',
        'employer__name',
        'employer__location',
    ]
    filterset_fields = [
        'owner__following__followed__profile',
        'owner__followed__owner__profile',
        # colleague filter
        'employer__current_employee',
    ]


class ProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Allows the retrieval of a profile and the ability to
    edit it if the user is the owner.
    """
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.annotate(
        posts_count=Count('owner__post', distinct=True),
        followers_count=Count('owner__followed', distinct=True),
        following_count=Count('owner__following', distinct=True),
        approval_count=Count('approval__owner', distinct=True),
    ).order_by('-created_on')

    def destroy(self, request, *args, **kwargs):
        profile = self.get_object()

        # Check if the current user is the owner of the profile
        if not request.user == profile.owner:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Delete the profile
        profile.delete()

        # Delete the user instance
        request.user.delete()

        # Log the user out
        django_logout(request)

        return Response(status=status.HTTP_204_NO_CONTENT)

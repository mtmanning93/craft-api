from django.db.models import Count
from rest_framework import status
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Profile
from .serializers import ProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from craft_api.permissions import IsOwnerOrReadOnly
from rest_framework.views import APIView
from django.http import Http404
from craft_api.views import logout_route
from django.contrib.auth.models import User


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
        'employer__current_employee',
    ]


class ProfileDetail(generics.RetrieveUpdateAPIView):
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

# WORKS BUT MUST TEST // Doesnt work with logout route
class DeleteAccount(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = self.request.user

        # Check if the user has a profile
        try:
            profile = Profile.objects.get(owner=user)
        except Profile.DoesNotExist:
            raise Http404("Profile not found for the user.")

        # Delete the user and associated profile
        user.delete()
        profile.delete()
        logout_route(request._request)

        return Response({"result": "User and profile deleted."}, status=status.HTTP_200_OK)

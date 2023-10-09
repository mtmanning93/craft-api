from rest_framework.views import APIView
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response

from .models import Profile
from .serializers import ProfileSerializer
from craft_api.permissions import IsOwnerOrReadOnly


class ProfileList(APIView):
    """
    List all profiles
    No post method as profile creation is handled by django signals
    in the models.py create_profile method.
    """
    def get(self, request):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(
            profiles, many=True, context={'request': request}
            )
        return Response(serializer.data)


class ProfileDetail(APIView):
    """
    Allows the retrieval of a profile and the ability to
    edit it if the user is the owner.
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            profile = Profile.objects.get(pk=pk)
            self.check_object_permissions(self.request, profile)
            return profile
        except Profile.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        profile = self.get_object(pk)
        serializer = ProfileSerializer(
            profile, context={'request': request}
            )
        return Response(serializer.data)

    def put(self, request, pk):
        profile = self.get_object(pk)
        serializer = ProfileSerializer(
            profile, data=request.data, context={'request': request}
            )
        
        if serializer.is_valid():
            serializer.save()
            print(f"USERS_ = {profile.employer}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

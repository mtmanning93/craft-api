from rest_framework.views import APIView
from django.http import Http404
from rest_framework import status, permissions
from rest_framework.response import Response

from .models import Company
from .serializers import CompanySerializer
from craft_api.permissions import IsOwnerOrReadOnly


class CompanyList(APIView):
    """
    Lists all companies.
    Allows a single user to create a maximum of 3 companies.
    """
    serializer_class = CompanySerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]

    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanySerializer(
            companies, many=True, context={'request': request}
        )
        return Response(serializer.data)

    def post(self, request):
        companies_count = Company.objects.filter(owner=request.user).count()

        if companies_count >= 3:
            return Response(
                {
                    "message": (
                        "You have reached the max profile "
                        "limit of 3 companies."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        company_title = request.data.get('name')
        company_location = request.data.get('location')

        existing_company = Company.objects.filter(
            name=company_title,
            location=company_location
        ).first()

        if existing_company:
            return Response(
                {
                    "message": (
                        f"A company with the title '{company_title}'"
                        f" and location '{company_location}' already exists."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CompanySerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class CompanyDetail(APIView):
    """
    Lists all company details.
    Allows the company instance owner to edit the details, as well
    as delete the company instance.
    """
    serializer_class = CompanySerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            company = Company.objects.get(pk=pk)
            self.check_object_permissions(self.request, company)
            return company
        except Company.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        company = self.get_object(pk)
        serializer = CompanySerializer(
            company, context={'request': request}
            )
        return Response(serializer.data)

    def put(self, request, pk):
        company = self.get_object(pk)
        serializer = CompanySerializer(
            company, data=request.data, context={'request': request}
            )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        company = self.get_object(pk)
        company.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

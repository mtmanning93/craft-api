from django.db.models import Count
from rest_framework import serializers, permissions, generics, filters
from .models import Company
from .serializers import CompanySerializer
from craft_api.permissions import IsOwnerOrReadOnly


class CompanyList(generics.ListCreateAPIView):
    """
    Lists all companies.
    Allows a single user to create a maximum of 3 companies.
    Validates if company is already in the list or not.
    """
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Company.objects.annotate(
        employee_count=Count('current_employee', distinct=True)
    ).order_by('created_on')
    filter_backends = [
        filters.OrderingFilter
    ]
    ordering_fields = [
        'employee_count'
    ]

    def validate_company(self, company_title, company_location):
        """
        Validates Company creation.
        If company is already in the list a ValidationError is raised.
        If owner already has 3 companies in the ölist a ValidationError
        is raised.
        """
        # Check the user's company count
        companies_count = Company.objects.filter(
            owner=self.request.user).count()

        if companies_count >= 3:
            raise serializers.ValidationError(
                "You have reached the max profile limit of 3 companies."
            )

        # Check if a company with the same title and location exists
        existing_company = Company.objects.filter(
            name=company_title,
            location=company_location
        ).first()

        if existing_company:
            raise serializers.ValidationError(
                f"A company with the title '{company_title}'"
                f" and location '{company_location}' already exists."
            )

    def perform_create(self, serializer):
        """
        Creates a company but first validates the company input.
        """
        company_title = serializer.validated_data.get('name')
        company_location = serializer.validated_data.get('location')
        self.validate_company(company_title, company_location)

        serializer.save(owner=self.request.user)


class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Lists all company details.
    Allows the company instance owner to edit the details, as well
    as delete the company instance.
    """
    serializer_class = CompanySerializer
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Company.objects.annotate(
        employee_count=Count('current_employee', distinct=True)
    ).order_by('created_on')

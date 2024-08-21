from django.shortcuts import render

# Create your views here.
import random, re, uuid
import string
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import GenerateUniqueTrackingNumber
from .serializers import GenerateTrackingNumberSerializer
from django.db import transaction
from datetime import datetime, timezone

class UniqueTrackingNumber(APIView):
    
    def get(self, request, *args, **kwargs):
        
        origin_country_id = request.query_params.get('origin_country_id')
        destination_country_id = request.query_params.get('destination_country_id')
        weight = request.query_params.get('weight')
        created_at = request.query_params.get('created_at')
        customer_id = request.query_params.get('customer_id')
        customer_name = request.query_params.get('customer_name')
        customer_slug = request.query_params.get('customer_slug')

        missing_params_list = []
        if not origin_country_id:
            missing_params_list.append('origin_country_id')
        if not destination_country_id:
            missing_params_list.append('destination_country_id')
        if not weight:
            missing_params_list.append('weight')
        if not created_at:
            missing_params_list.append('created_at')
        if not customer_id:
            missing_params_list.append('customer_id')
        if not customer_name:
            missing_params_list.append('customer_name')
        if not customer_slug:
            missing_params_list.append('customer_slug')
        
        if missing_params_list:
            return Response(
            {
                'error': f'The following required Query Parameters are missing: {", ".join(missing_params_list)}',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # print(customer_name)
        

        if not (self.validate_country_code(origin_country_id) and self.validate_country_code(destination_country_id)):
            return Response({'error': 'Invalid country code format. Must be in ISO 3166-1 alpha-2 format.',
                             'success': False}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            weight_in_float = float(weight)
            
            if weight_in_float <= 0:
                raise ValueError("Weight must be a positive number.")
            
            if '.' in weight:
                integer_part, decimal_part = weight.split('.')
                
                # print(len(decimal_part))
                if len(decimal_part) != 3:
                    raise ValueError("Weight must be a positive number with up to exact three decimal places.")
            else:
                raise ValueError("Weight must be a positive number with up to exact three decimal places.")

        except (ValueError, IndexError):
            return Response({'error': 'Invalid weight format. Must be a positive number with up to three decimal places.',
                             'success': False}, status=status.HTTP_400_BAD_REQUEST)
        
        
        # Validation for created_at RFC format
        if not self.validate_rfc3339(created_at):
            return Response({'error': 'Invalid created_at format. Must be RFC 3339.',
                             'success': False}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validation for customer ID UUID format
        try:
            uuid.UUID(customer_id)
        except ValueError:
            return Response({'error': 'Invalid customer_id format. Must be a valid UUID.',
                             'success': False}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validation for customer Name
        if not self.validate_customer_name(customer_name):
            return Response({'error': 'Invalid customer_name format. Must contain only alphabets.',
                             'success': False}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate Customer slug
        if not self.validate_slug(customer_slug):
            return Response({'error': 'Invalid customer_slug format. Must be slug-case/kebab-case.',
                             'success': False}, status=status.HTTP_400_BAD_REQUEST)
                    
        try:
            tracking_number = self.generate_unique_tracking_number()
            
            with transaction.atomic():
                tracking_number_record = GenerateUniqueTrackingNumber.objects.create(
                    tracking_number=tracking_number,
                    origin_country_id=origin_country_id,
                    destination_country_id=destination_country_id,
                    weight=weight,
                    created_at=created_at,
                    customer_id=customer_id,
                    customer_name=customer_name,
                    customer_slug=customer_slug
                )
                
            formatted_created_at = tracking_number_record.created_at.isoformat()


            serializer = GenerateTrackingNumberSerializer(tracking_number_record)
            
            return Response({
                'tracking_number': tracking_number_record.tracking_number,
                'created_at': formatted_created_at,
                'success': True
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
    def validate_country_code(self, country_code):

        return re.match(r'^[A-Z]{2}$', country_code) is not None
    
    def validate_slug(self, customer_slug):

        return re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', customer_slug) is not None
    
    def validate_rfc3339(self, timestamp):

        rfc3339_pattern = re.compile(
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|([+-]\d{2}:\d{2}))$'
        )
        return bool(rfc3339_pattern.match(timestamp))
    
    def validate_customer_name(self, name):

        return re.match(r'^[A-Za-z\s]+$', name) is not None
    
    def generate_unique_tracking_number(self):
        pattern = r'^[A-Z0-9]{1,16}$'
        counter = 0
        max_retry = 10  # To prevent infinite loops

        while counter < max_retry:
            tracking_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

            if re.match(pattern, tracking_number) and not GenerateUniqueTrackingNumber.objects.filter(tracking_number=tracking_number).exists():
                return tracking_number

            counter += 1

        raise Exception('Unable to generate unique tracking number. Please try again')
        

        
        
        




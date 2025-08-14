from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.http import Http404


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    custom_response_data = {
        'success': False,
        'message': 'An error occurred',
        'errors': {},
        'data': None
    }
    
    if response is not None:
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, dict):
                custom_response_data['errors'] = exc.detail
                custom_response_data['message'] = 'Validation failed'
            elif isinstance(exc.detail, list):
                custom_response_data['message'] = exc.detail[0] if exc.detail else 'Error occurred'
            else:
                custom_response_data['message'] = str(exc.detail)
        
        custom_response_data['status_code'] = response.status_code
        response.data = custom_response_data
    
    return response


def success_response(data=None, message='Success', status_code=status.HTTP_200_OK):
    return Response({
        'success': True,
        'message': message,
        'data': data,
        'errors': {}
    }, status=status_code)


def error_response(message='Error occurred', errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({
        'success': False,
        'message': message,
        'data': None,
        'errors': errors or {}
    }, status=status_code)

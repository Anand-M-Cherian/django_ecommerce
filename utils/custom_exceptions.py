from rest_framework.views import exception_handler
from http import HTTPStatus
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)
    
    if response is not None:
        http_code_to_message = {
            status_code.value: status_code.description
            for status_code in HTTPStatus
        }

        # Create a model for the error payload
        # This will be used to structure the error response
        error_payload = {
            'error': {
                "status_code": 0,
                "message": "",
                "details": []
            }
        }

        error = error_payload['error']
        status_code = response.status_code

        # Set the values for the error payload
        error['status_code'] = response.status_code
        error['message'] = http_code_to_message.get(status_code, "An unexpected error occurred.")
        error['details'] = response.data

        # Overwrite the response data with the error payload
        response.data = error_payload
        return response
    
    else:
        error = {
            "error": "Oops!!! Some internal error has occured in out system. Please try again later."
        }

        return Response(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
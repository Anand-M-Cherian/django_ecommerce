from django.http import JsonResponse

def handle_404(request, exception):

    message = ('The requested url route was not found on this server. ')
    response = JsonResponse(data={'error': message})
    response.status_code = 404
    return response

def handle_500(request):

    message = ('An unexpected error occurred on the server. Please try again later. ')
    response = JsonResponse(data={'error': message})
    response.status_code = 500
    return response
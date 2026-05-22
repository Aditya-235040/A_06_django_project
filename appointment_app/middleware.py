from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class RoleAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            path = request.path
            role = request.user.role

            # Define role-specific path prefixes
            role_paths = {
                'ADMIN': '/admin-portal/',
                'PROVIDER': '/provider/',
                'CUSTOMER': '/customer/',
            }

            # If user tries to access a path not meant for their role
            # (Basic check: if it starts with another role's prefix)
            for other_role, prefix in role_paths.items():
                if other_role != role and path.startswith(prefix):
                    messages.error(request, "You do not have permission to access this area.")
                    
                    # Redirect to their own dashboard
                    if role == 'ADMIN':
                        return redirect('admin_dashboard')
                    elif role == 'PROVIDER':
                        return redirect('provider_dashboard')
                    else:
                        return redirect('customer_dashboard')

        response = self.get_response(request)
        return response

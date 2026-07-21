import uuid

from django.contrib.auth import logout
from django.shortcuts import redirect


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

def logout_view(request):
    logout(request)
    return redirect('logged_out')

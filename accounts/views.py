from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def admin_login_view(request):
    """
    Dedicated Corporate Administrator Login.
    Separate from student interface, strictly for authorized assessment controllers.
    """
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        login_id = request.POST.get('username_or_email', '').strip()
        password = request.POST.get('password', '').strip()

        # Support login by username or email
        user_obj = None
        if '@' in login_id:
            user_obj = User.objects.filter(email__iexact=login_id).first()
            username = user_obj.username if user_obj else None
        else:
            username = login_id

        user = authenticate(request, username=username, password=password) if username else None

        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}. Authorized Session Active.")
            next_url = request.GET.get('next', 'admin_dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid administrator credentials or unauthorized account.")

    context = {
        'page_title': 'Administrator Portal Sign-In — KORLANCE'
    }
    return render(request, 'accounts/admin_login.html', context)


def admin_logout_view(request):
    """
    Secure Administrator Sign-Out.
    """
    logout(request)
    messages.info(request, "Administrator session terminated safely.")
    return redirect('admin_login')

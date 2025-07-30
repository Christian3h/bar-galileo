from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from roles.models import UserProfile, Role
from roles.forms import UserProfileForm
from django.db.models import Case, When, Value, IntegerField

def user_list(request):
    users = User.objects.all().select_related('userprofile')
    # Ordenar: usuarios con rol al final
    users = users.annotate(
        is_user_role=Case(
            When(userprofile__rol__nombre='usuario', then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).order_by('is_user_role', 'username')
    roles = Role.objects.all()
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        rol_id = request.POST.get('rol_id')
        user = User.objects.get(id=user_id)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.rol_id = rol_id
        profile.save()
        return redirect('users:user_list')
    return render(request, 'users/user_list.html', {'users': users, 'roles': roles})

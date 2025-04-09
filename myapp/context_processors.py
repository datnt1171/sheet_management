def user_groups(request):
    if request.user.is_authenticated:
        return {
            'is_crud_user': request.user.groups.filter(name='CRUD').exists(),
            'is_view_user': request.user.groups.filter(name='View').exists(),
        }
    return {}
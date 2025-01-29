def profile_pic_processor(request):
    if request.user.is_authenticated:
        try:
            profile_pic_url = request.user.profile.profile_pic.url if request.user.profile.profile_pic else '/static/images/default.jpg'
        except Exception:
            profile_pic_url = '/static/images/default.jpg'
        return {'profile_pic_url': profile_pic_url}
    return {'profile_pic_url': '/static/images/default.jpg'}

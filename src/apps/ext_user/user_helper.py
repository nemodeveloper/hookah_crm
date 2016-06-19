from src.apps.ext_user.models import WorkProfile


def is_employer(user):

    if not user:
        return False

    if WorkProfile.objects.filter(ext_user=user).first():
        return True
    return False

from datetime import datetime

from src.apps.ext_user.models import WorkSession, WorkProfile


def create_open_work_session(user):

    work_session = WorkSession(ext_user=user, session_status='OPEN')
    work_session.start_workday = datetime.now()
    work_session.save()


def close_open_work_session(user):

    work_sessions = WorkSession.objects.filter(ext_user=user, session_status='OPEN')
    if work_sessions:
        for work_session in work_sessions:
            work_session.close_session()


def is_employer(user):

    if not user or user.is_anonymous:
        return False

    if WorkProfile.objects.filter(ext_user=user).first():
        return True
    return False

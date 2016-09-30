from datetime import datetime

from src.apps.ext_user.models import WorkSession, WorkProfile


def create_open_work_session(user):

    work_session = WorkSession(ext_user=user, session_status='OPEN')
    work_session.start_workday = datetime.now()
    work_session.save()


def close_open_work_session(user):

    work_session = WorkSession.objects.filter(ext_user=user, session_status='OPEN').first()
    if work_session:
        cur_date = datetime.now()
        if cur_date.hour >= 23 or cur_date.hour < 10:
            work_session.session_status = 'OVER'
        else:
            work_session.session_status = 'CLOSE'
        work_session.end_workday = cur_date
        work_session.save()


def is_employer(user):

    if not user:
        return False

    if WorkProfile.objects.filter(ext_user=user).first():
        return True
    return False
from datetime import datetime

from src.apps.ext_user.models import WorkSession


def create_open_work_session(user):

    work_session = WorkSession(ext_user=user, session_status='OPEN')
    work_session.start_workday = datetime.now()
    work_session.save()


def close_open_work_session(user):

    work_session = WorkSession.objects.filter(ext_user=user, session_status='OPEN').first()
    if work_session:
        work_session.session_status = 'CLOSE'
        work_session.end_workday = datetime.now()
        work_session.save()

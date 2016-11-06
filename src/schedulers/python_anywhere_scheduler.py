from src.schedulers.schedulers import create_db_fixture


def start_create_db_fixture_task():
    create_db_fixture()


start_create_db_fixture_task()


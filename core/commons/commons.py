import random
import string
import uuid
from datetime import datetime, date, time

import pytz

from .exception import CustomException

STATUSUSER = {
    'ENABLE': 'Active',
    'DISABLE': 'Desactive',
    'ARCHIVE': 'Archivé',
    'CANCEL': 'Supprimé',
    'PENDING_KYC': 'Demande KYC',
    'VALID_KYC': 'Valider KYC',
    'REJECT_KYC': 'Rejeter KYC'
}
STATUS = {
    'ENABLE': 'Active',
    'DISABLE': 'Desactive',
    'ARCHIVE': 'Archivé',
    'CANCEL': 'Supprimé'
}

IMAGETYPE = {
    ('FONT', 'Devant'),
    ('LIST', 'liste'),
}


def convert_string_to_date(str_date: str)->date:
    try:
        return datetime.strptime(str_date, '%d-%m-%Y').date()
    except ValueError:
        raise CustomException(
            message="Erreur sur le format. exemple 12-12-2024",
            status=400)



def convert_date_to_str(date_input: date):
    try:
        return date_input.strftime('%d-%m-%Y')
    except ValueError:
        raise CustomException(
            message="Erreur sur le formatage de la date",
            status=400)


def convert_string_to_datetime(str_date: str):
    try:
        return datetime.strptime(str_date, '%d-%m-%Y %H:%M:%S')
    except ValueError:
        raise CustomException(
            message="Erreur sur le format. exemple 12-12-2024 12:12:12",
            status=400)


def convert_string_to_startDate(str_date: str):
    try:
        date = datetime.strptime(str_date, '%d-%m-%Y').date()
        return datetime.now().replace(year=date.year, month=date.month, day=date.day, hour=0, minute=0, second=0,
                                         tzinfo=pytz.UTC)
    except ValueError:
        raise CustomException(
            message="Erreur sur le format. exemple 12-12-2024 12:12:12",
            status=400)


def convert_string_to_end_date(str_date: str):
    try:
        date = datetime.strptime(str_date, '%d-%m-%Y').date()
        return datetime.now().replace(year=date.year, month=date.month, day=date.day, hour=23, minute=59, second=59,
                                         tzinfo=pytz.UTC)

    except ValueError:
        raise CustomException(
            message="Erreur sur le format. exemple 12-12-2024 12:12:12",
            status=400)


def convert_datetime_to_str(datetime_input: datetime):
    try:

        return '' if datetime_input == '' else datetime_input.strftime('%d-%m-%Y %H:%M:%S')
    except ValueError:
        raise CustomException(
            message="Erreur sur le format. exemple 12-12-2024 12:12:12",
            status=400)


def convert_string_to_time(str_date: str):
    try:
        return datetime.strptime(str_date, '%H:%M:%S').time()
    except ValueError:
        raise CustomException(
            message="Erreur sur le format. exemple 12:12:12",
            status=400)


def convert_time_to_str(time_input: time):
    try:
        return time_input.strftime('%H:%M:%S')
    except ValueError:
        raise CustomException(
            message="Erreur sur le formatage de l'heure.",
            status=400)


def generate_code(size: int):
    uu = uuid.uuid4()
    return str(uu.fields[-1])[:size]


def generate_password_tmp(size: int):
    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
    return str(res)

def generate_slug(name: str, identity: str):
    from django.utils.text import slugify
    return f"{slugify(name)}-{identity}"
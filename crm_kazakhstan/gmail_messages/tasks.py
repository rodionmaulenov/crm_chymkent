import imaplib
import os

from datetime import timedelta, datetime
from celery import shared_task

from django.db import models

from gmail_messages.service_inbox import InboxMessages
from mothers.models import Mother

current_directory = os.path.dirname(os.path.abspath(__file__))

directory = os.path.join(current_directory, 'last_index')
file = os.path.join(directory, 'last_index.txt')

email_user = "alina.rodion123@gmail.com"
email_pass = "wlcpfrqopczlvubc "
email_server = "imap.gmail.com"
email_chapter = 'inbox'

date = datetime.today()
search_criteria = (f'SINCE "{date.strftime("%d-%b-%Y")}" '
                   f'BEFORE "{(date + timedelta(days=1)).strftime("%d-%b-%Y")}"')

translation_dict = {
    'ФИО': 'name',
    'Телефон': 'number',
    'Город проживания': 'residence',
    'Программа': 'program',
    'Ваш рост и вес': 'height_and_weight',
    'Есть ли склонность ко вредным привычкам?': 'bad_habits',
    'Делали Вам кесарево? Сколько раз?': 'caesarean',
    'Возраст родных детей': 'children_age',
    'Ваш возраст': 'age',
    'Гражданство': 'citizenship',
    'Группа крови': 'blood',
    'Семейное положение': 'maried',
}

Mother: models


@shared_task
def save_message():
    inbox = InboxMessages()
    try:
        inbox.login_gmail(email_user, email_pass, email_server, email_chapter)
        inbox.search_condition(search_criteria)

        for pk in inbox.email_ids:
            try:
                Mother.objects.get(pk=pk)
            except Mother.DoesNotExist:
                inbox(pk)

        for email in inbox.extract_message():
            mother_data = inbox.get_body_email(translation_dict, email)
            Mother.objects.create(**mother_data)

        inbox.not_proceed_emails.clear()
        # Close the mailbox
        inbox.mail.logout()
    except IndexError:
        # Close the mailbox
        inbox.mail.logout()
    except imaplib.IMAP4.error:
        # Close the mailbox
        inbox.mail.logout()

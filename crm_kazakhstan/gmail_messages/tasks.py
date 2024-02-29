import imaplib
import os

from datetime import timedelta
from celery import shared_task
from guardian.shortcuts import assign_perm

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from gmail_messages.service_inbox import InboxMessages

from mothers.models import Mother, State, Stage

User = get_user_model()

Mother: models
State: models
Stage: models

current_directory = os.path.dirname(os.path.abspath(__file__))

directory = os.path.join(current_directory, 'last_index')
file = os.path.join(directory, 'last_index.txt')

email_user = "alina.rodion123@gmail.com"
email_pass = "wlcpfrqopczlvubc "
email_server = "imap.gmail.com"
email_chapter = 'inbox'

date = timezone.now()
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

            mother = Mother.objects.create(**mother_data)

            # at once create related models
            State.objects.create(mother=mother, condition=State.ConditionChoices.CREATED, finished=True)
            Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

            # Get or create the group
            rushane = User.objects.get(username='Rushana')

            # Assign permission for each instance of Mother
            assign_perm('view_mother', rushane, mother)
            assign_perm('change_mother', rushane, mother)

        inbox.not_proceed_emails.clear()
        # Close the mailbox
        inbox.mail.logout()
    except IndexError:
        # Close the mailbox
        inbox.mail.logout()
    except imaplib.IMAP4.error:
        # Close the mailbox
        inbox.mail.logout()

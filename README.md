# Surrogate Mother CRM

## Description 
The Surrogate Mother CRM is designed to streamline the management of questionnaires from potential surrogate mothers. It efficiently handles personal information inflow and categorizes it through various stages of a surrogate program, tracking each surrogate mother's journey from entry into the program until birth.

## Usage Documents application
### User's permission:
- For only view documents user must have the view_documentproxy permission.
- The user which has assigned mother instances can see this objs and do some operations on it.
- Superuser can do anything.

### User's access:
- Has access for all mothers instances and actions which filter mother list based on stage.
- Can add, change, delete new documents on mother instance.
- Superuser can do anything.




## Models
1. **Mother**: Manages surrogate mother profiles, including personal details and program status.
2. **Condition**: Tracks conditions or stages a surrogate mother may go through, including status, reasons, and scheduled appointments.

## Features and Customizations
- **Timezone Middleware**: Adjusts timezone based on the authenticated user's timezone.
- **Automated Email Processing (Celery Task)**: Automates checking Gmail every minute to retrieve and save data from emails directly into the `Mother` model.
- **Admin Interface Customization**
- **MotherAdmin**: Enhances the Django admin interface with tailored inline editing, custom queryset handling, advanced search, local time conversion, and specific actions.
- **Advanced Inline Admin Customization (ConditionInline)**: Provides a sophisticated interface for managing `Condition` instances related to `Mother`, featuring dynamic form behavior and custom rendering.
- **Custom Filters for Enhanced Querying**: 
 - `ConditionListFilter` and `AuthConditionListFilter`: Custom filters for querying `Mother` instances based on specific conditions and user permissions.
 - `ReturnedFromFirstVisitListFilter` and `AuthReturnedFromFirstVisitListFilter`: Filters to identify mothers who have returned from the first visit stage, with access controlled by user permissions.


## Roadmap
Future developments and enhancements will be added here.



## Requirements
- Django (3.2 - <4.0)
- Python-decouple (3.8)
- Celery with Redis (5.3.4)
- Django-Celery-Beat (2.5.0)
- Psycopg2-Binary (2.9.9)
- Flower (1.2.0)
- Freezegun (0.3.4)
- Django-Timezone-Field (6.1.0)

## Installation Instructions
1. **Clone the Repository**
git clone git@github.com:rodionmaulenov/crm_chymkent.git
2. **Set up a Virtual Environment**
python -m venv venv
source venv/bin/activate # On Windows use venv\Scripts\activate
3. **Install Required Packages**
pip install -r requirements.txt


# from django.contrib import admin
#
# from documents.models import Document
#
#
# class DocumentAdmin(admin.ModelAdmin):
#     list_display = ('name', 'mother', 'document')
#     fields = ('mother', 'name', ecute_from_command_line(sys.argv)
#   File "/home/rodion/Desktop/crm_chymkent/venv/lib/python3.10/site-packages/django/core/management/__init__.py", line 419, in execute_from_command_line
#     utility.execute()
#   File "/home/rodion/Desktop/crm_chymkent/venv/lib/python3.10/site-packages/django/core/management/__init__.py", line 413, in execute
#     self.fetch_command(subcommand).run_from_argv(self.argv)
#   File "/home/rodion/Desktop/crm_chymkent/venv/lib/python3.10/site-packages/django/core/management/commands/test.py", line 23, in run_from_argv
#     super().run_from_argv(argv)
#   File "/home/rodion/Desktop/crm_chymkent/venv/lib/python3.10/site-packages/django/core/management/base.py", line 354, in run_from_argv
#     self.execute(*args, **cmd_options)
#   File "/home/rodion/Desktop/crm_chymkent/venv/lib/python3.10/site-packages/django/core/management/base.py", line 398, in execute
#     output = self.handle(*args, **options)
#   File "/home/rodion/Desktop/crm_chymkent/venv/lib/python3.10/site-packages/django/core/management/commands/test.py", line 55, in handle
#     failures = test_runner.run_tests(test_labels)
#   File "/home/rodion/Desktop/crm_chymkent/venv/lib/python3.10/site-packages/django/test/runner.py", line 725, in run_tests
#     old_config = self.setup_databases(aliases=databases)
#   File "/home/rodion/Desktop/crm_chymkent/venv/lib/python3.10/site-packages/django/test/runner.py", line 643, in setup_databases
#     return _setup_databases(
#   File "/home/rodion/Desktop/crm_chymkent/venv/lib/python3.10/site-packages/django/test/utils.py", line 179, in setup_databases
#     connection.creation.create_test_db(
#   File "/home/rodion/Desktop/crm_chymkent/venv/lib/python3.10/site-packages/django/db/backends/base/creation.py", line 90, in create_test_db
#     self.connection._test_serialized_contents = self.serialize_db_to_string()
#   File "/home/rodion/Desktop/crm_chymkent/venv/lib/python3.10/site-packages/django/db/backends/base/creation.py", line 136, in serialize_db_to_string
#     serializers.serialize("json", get_objects(), indent=None, stream=out)
#   File "/home/rodion/Desktop/crm_chymkent/venv/lib/python3.10/site-packages/django/core/serializers/__init__.py", line 129, in serialize
#     s.serialize(queryset, **options)
#   File "/home/rodion/Desktop/crm_chymkent/venv/lib/python3.10/site-packages/django/core/serializers/base.py", line 90, in serialize
#     for count, obj in enumerate(queryset, start=1):
#   File "/home/rodion/Desktop/crm_chymkent/venv/lib/python3.10/site-packages/django/db/backends/base/creation.py", line 133, in get_objects
#     yield from queryset.iterator()
#   File "/home/rodion/Desktop/crm_chymkent/venv/lib/python3.10/site-packages/django/db/models/query.py", line 353, in _iterator
#     yield from self._iterable_class(self, chunked_fetch=use_chunked_fetch, chunk_size=chunk_size)
#   File "/home/rodion/Desktop/crm_chymkent/venv/lib/python3.10/site-packages/django/db/models/query.py", line 51, in __iter__
#     results = compiler.execute_sql(chunked_fetch=self.chunked_fetch, chunk_size=self.chunk_size)
#   File "/home/rodion/Desktop/crm_chymkent/venv/lib/python3.10/site-packages/django/db/models/sql/compiler.py", line 1178, in execute_sql
#     cursor.close()
# psycopg2.errors.InvalidCursorName: cursor "_django_curs_127490373939648_sync_17" does not exist
# 'document')
#
#
# admin.site.register(Document, DocumentAdmin)
#
#
# class DocumentInline(admin.StackedInline):
#     model = Document
#     extra = 0  # Number of empty forms to display
#     raw_id_fields = ('mother',)

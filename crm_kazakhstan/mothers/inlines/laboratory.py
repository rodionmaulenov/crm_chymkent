from django.contrib import admin
from mothers.models.mother import Laboratory, LaboratoryFile
from mothers.services.application import convert_utc_to_local
from django.utils.html import format_html


class LaboratoryInline(admin.TabularInline):
    model = Laboratory
    fields = 'mother', 'custom_scheduled_time', 'custom_analysis_types', 'custom_video', 'description', 'is_completed',
    readonly_fields = 'custom_scheduled_time', 'custom_analysis_types', 'custom_video', 'description', 'is_completed'

    class Media:
        js = 'laboratory/js/hide_p_elements.js', 'laboratory/js/move_text_on_second_line.js'

    def get_queryset(self, request):
        self.request = request
        return super().get_queryset(request)

    def has_view_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False

    def custom_scheduled_time(self, obj):
        local_datetime = convert_utc_to_local(self.request, obj.scheduled_time)
        formatted_time = local_datetime.strftime("%d %B, %A %H:%M")
        return formatted_time

    custom_scheduled_time.short_description = 'Scheduled Time'

    def custom_analysis_types(self, laboratory):
        files = ''
        related_to_lab_analysis = laboratory.analysis_types.all()
        for analysis in related_to_lab_analysis:
            laboratory_files = LaboratoryFile.objects.filter(laboratory=laboratory, analysis_type=analysis)
            for num, laboratory_file in enumerate(laboratory_files):
                if laboratory_file.file:
                    name = laboratory_file.analysis_type.name
                    files += f'{num + 1}. File: <a href="{laboratory_file.file.url}" target="_blank">{name}</a><br>'
        return format_html(files)

    custom_analysis_types.short_description = 'Analysis'

    def custom_video(self, laboratory):
        files = ''
        laboratory_video_instances = laboratory.videos_laboratory.all()
        for num, laboratory_video in enumerate(laboratory_video_instances):

            if laboratory_video.ultrasound_video:
                video_url = laboratory_video.ultrasound_video.url
                video_name = laboratory_video.ultrasound_video.name.split('/')[-1]
                files += f'{num + 1}. Video file: <a href="{video_url}" target="_blank">{video_name}</a><br>'

            if laboratory_video.ultrasound_file:
                name = laboratory_video.ultrasound_file.name.split('/')[-1]
                files += f'{num + 1}. File: <a href="{laboratory_video.ultrasound_file.url}" target="_blank">{name}</a><br>'
        return format_html(files)

    custom_video.short_description = 'Video'

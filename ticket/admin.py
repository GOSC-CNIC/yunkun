from django.contrib import admin

from utils.model import BaseModelAdmin
from .models import (
    Ticket, TicketChange, FollowUp, TicketRating
)


@admin.register(Ticket)
class TicketAdmin(BaseModelAdmin):
    list_display = ('id', 'title', 'status', 'service_type', 'severity', 'submitter', 'submit_time',
                    'contact', 'assigned_to')
    list_display_links = ('id', 'title')
    list_filter = ('service_type', 'status', 'severity')
    search_fields = ('title',)
    list_select_related = ('submitter', 'assigned_to')

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(FollowUp)
class FollowUpAdmin(BaseModelAdmin):
    list_display = ('id', 'ticket', 'user', 'submit_time', 'fu_type', 'title', 'ticket_change')
    list_display_links = ('id',)
    list_filter = ('fu_type', )
    search_fields = ('title', 'ticket__id')
    list_select_related = ('user', 'ticket_change')


@admin.register(TicketChange)
class TicketChangeAdmin(BaseModelAdmin):
    list_display = ('id', 'ticket_field', 'display')
    list_display_links = ('id',)
    search_fields = ('id',)


@admin.register(TicketRating)
class TicketRatingAdmin(BaseModelAdmin):
    list_display = ('id', 'ticket_id', 'score', 'submit_time', 'username', 'is_sys_submit')
    list_display_links = ('id',)
    search_fields = ('id', 'ticket_id')
    list_filter = ('is_sys_submit',)

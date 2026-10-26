from django.contrib import admin
from .models import Property, Experience, Guest, Booking


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'price', 'capacity', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('name', 'location')


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('name',)


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email', 'phone')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'guest',
        'property',
        'check_in',
        'check_out',
        'guests',
        'status',
        'created_at'
    )
    list_filter = ('status', 'check_in', 'check_out')
    search_fields = (
        'guest__name',
        'guest__email',
        'property__name'
    )
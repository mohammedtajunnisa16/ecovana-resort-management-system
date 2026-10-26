from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("", views.home, name="home"),
    path("stays/", views.stays, name="stays"),
    path("experiences/", views.experiences, name="experiences"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("booking/", views.booking, name="booking"),
    path('reservation-success/<int:booking_id>/',views.reservation_success,name='reservation_success'),
    path('management/',views.management_dashboard,name='management_dashboard'),
    path( 'management/properties/', views.management_properties, name='management_properties'),
    path('management/properties/add/',views.add_property,name='add_property'),
    path('management/properties/<int:property_id>/edit/', views.edit_property, name='edit_property'),
    path('management/reservations/', views.management_reservations, name='management_reservations'),
    path('management/reservations/<int:booking_id>/', views.reservation_detail, name='reservation_detail'),
    path('management/reservations/<int:booking_id>/confirm/', views.confirm_booking, name='confirm_booking'),
    path('management/reservations/<int:booking_id>/reject/', views.reject_booking, name='reject_booking'),
    path('management/guests/', views.management_guests, name='management_guests'),
    path('management/experiences/', views.management_experiences, name='management_experiences'),
    path('management/experiences/<str:experience_name>/edit/', views.edit_experience, name='edit_experience'),
]
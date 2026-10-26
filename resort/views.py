from django.shortcuts import render,redirect,get_object_or_404
from .models import Property, Guest, Booking, Experience
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db.models import Count
def manager_required(user):
    return user.is_staff


def home(request):
    return render(request, "home.html")
def experiences(request):
    return render(request, "experiences.html")

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")



def stays(request):
    properties = Property.objects.filter(is_available=True)
    return render(request, 'stays.html', {'properties': properties})

def booking(request):
    properties = Property.objects.filter(is_available=True)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        age = request.POST.get('age')
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        guest_type = request.POST.get('guest_type')
        property_id = request.POST.get('property')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        adults = request.POST.get('adults')
        children = request.POST.get('children', '0')
        message = request.POST.get('message', '').strip()
        guest_image = request.FILES.get('guest_image')

        if not all([name, age, phone, email, guest_type, property_id, check_in, check_out, adults]):
            messages.error(request, 'Please complete all required fields.')
            return render(request, 'booking.html', {'properties': properties})

        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, 'Please enter a valid 10-digit phone number.')
            return render(request, 'booking.html', {'properties': properties})

        try:
            age = int(age)
            adults = int(adults)
            children = int(children)
        except ValueError:
            messages.error(request, 'Please enter valid booking details.')
            return render(request, 'booking.html', {'properties': properties})

        if age < 1:
            messages.error(request, 'Please enter a valid age.')
            return render(request, 'booking.html', {'properties': properties})

        if adults < 1:
            messages.error(request, 'At least one adult is required.')
            return render(request, 'booking.html', {'properties': properties})

        try:
            property_obj = Property.objects.get(
                id=property_id,
                is_available=True
            )
        except Property.DoesNotExist:
            messages.error(request, 'The selected property is not available.')
            return render(request, 'booking.html', {'properties': properties})

        total_guests = adults + children

        if total_guests > property_obj.capacity:
            messages.error(
                request,
                f'{property_obj.name} can accommodate a maximum of {property_obj.capacity} guests.'
            )
            return render(request, 'booking.html', {'properties': properties})

        if check_out <= check_in:
            messages.error(request, 'Check-out date must be after check-in date.')
            return render(request, 'booking.html', {'properties': properties})

        if check_in < timezone.localdate().isoformat():
            messages.error(request, 'Check-in date cannot be in the past.')
            return render(request, 'booking.html', {'properties': properties})

        guest = Guest.objects.create(
            name=name,
            age=age,
            phone=phone,
            email=email,
            guest_type=guest_type
        )

        booking_obj = Booking.objects.create(
            guest=guest,
            property=property_obj,
            check_in=check_in,
            check_out=check_out,
            guests=total_guests,
            special_request=message,
            guest_image=guest_image,
            status='Pending'
        )

        return redirect(
            'reservation_success',
            booking_id=booking_obj.id
        )

    return render(
        request,
        'booking.html',
        {'properties': properties}
    )

def reservation_success(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    return render(
        request,
        'reservation_success.html',
        {'booking': booking}
    )

    #MANAGEMENT DASHBOARD


@login_required
@user_passes_test(manager_required)
def management_dashboard(request):
    total_properties = Property.objects.count()
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='Pending').count()
    confirmed_bookings = Booking.objects.filter(status='Confirmed').count()
    total_guests = Guest.objects.count()

    recent_bookings = Booking.objects.select_related(
        'guest',
        'property'
    ).order_by('-created_at')[:5]

    context = {
        'total_properties': total_properties,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'total_guests': total_guests,
        'recent_bookings': recent_bookings,
    }

    return render(
        request,
        'management/dashboard.html',
        context
    )

# =========================
# MANAGEMENT - PROPERTIES
# =========================

@login_required
@user_passes_test(manager_required)
def management_properties(request):

    properties = Property.objects.all().order_by('-id')

    return render(
        request,
        'management/properties.html',
        {
            'properties': properties
        }
    )


@login_required
@user_passes_test(manager_required)
def add_property(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        location = request.POST.get('location', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price')
        capacity = request.POST.get('capacity')
        bedrooms = request.POST.get('bedrooms')
        bathrooms = request.POST.get('bathrooms')
        image = request.FILES.get('image')
        is_available = request.POST.get('is_available') == 'on'

        if not all([name, location, description, price, capacity, bedrooms, bathrooms]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('add_property')

        try:
            price = float(price)
            capacity = int(capacity)
            bedrooms = int(bedrooms)
            bathrooms = int(bathrooms)
        except (ValueError, TypeError):
            messages.error(request, 'Please enter valid property details.')
            return redirect('add_property')

        if price <= 0:
            messages.error(request, 'Price must be greater than zero.')
            return redirect('add_property')

        if capacity < 1:
            messages.error(request, 'Capacity must be at least 1 guest.')
            return redirect('add_property')

        if bedrooms < 1 or bathrooms < 1:
            messages.error(request, 'Bedrooms and bathrooms must be at least 1.')
            return redirect('add_property')

        Property.objects.create(
            name=name,
            location=location,
            description=description,
            price=price,
            capacity=capacity,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            image=image,
            is_available=is_available
        )

        messages.success(
            request,
            f'{name} has been added successfully.'
        )

        return redirect('management_properties')

    return render(
        request,
        'management/add_property.html'
    )
@login_required
@user_passes_test(manager_required)
def edit_property(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        location = request.POST.get('location', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price')
        capacity = request.POST.get('capacity')
        bedrooms = request.POST.get('bedrooms')
        bathrooms = request.POST.get('bathrooms')
        image = request.FILES.get('image')
        is_available = request.POST.get('is_available') == 'on'

        if not all([name, location, description, price, capacity, bedrooms, bathrooms]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('edit_property', property_id=property_obj.id)

        try:
            price = float(price)
            capacity = int(capacity)
            bedrooms = int(bedrooms)
            bathrooms = int(bathrooms)
        except (ValueError, TypeError):
            messages.error(request, 'Please enter valid property details.')
            return redirect('edit_property', property_id=property_obj.id)

        if price <= 0:
            messages.error(request, 'Price must be greater than zero.')
            return redirect('edit_property', property_id=property_obj.id)

        if capacity < 1:
            messages.error(request, 'Capacity must be at least 1 guest.')
            return redirect('edit_property', property_id=property_obj.id)

        if bedrooms < 1 or bathrooms < 1:
            messages.error(request, 'Bedrooms and bathrooms must be at least 1.')
            return redirect('edit_property', property_id=property_obj.id)

        property_obj.name = name
        property_obj.location = location
        property_obj.description = description
        property_obj.price = price
        property_obj.capacity = capacity
        property_obj.bedrooms = bedrooms
        property_obj.bathrooms = bathrooms
        property_obj.is_available = is_available

        if image:
            property_obj.image = image

        property_obj.save()

        messages.success(request, f'{name} has been updated successfully.')
        return redirect('management_properties')

    return render(
        request,
        'management/edit_property.html',
        {'property': property_obj}
    )

@login_required
@user_passes_test(manager_required)
def management_reservations(request):
    total_reservations = Booking.objects.count()
    pending_reservations = Booking.objects.filter(status='Pending').count()
    confirmed_reservations = Booking.objects.filter(status='Confirmed').count()
    rejected_reservations = Booking.objects.filter(status='Rejected').count()

    selected_status = request.GET.get('status', 'all')

    if selected_status in ['Pending', 'Confirmed', 'Rejected']:
        bookings = Booking.objects.select_related(
            'guest',
            'property'
        ).filter(
            status=selected_status
        ).order_by('-created_at')
    else:
        selected_status = 'all'
        bookings = Booking.objects.select_related(
            'guest',
            'property'
        ).order_by('-created_at')

    context = {
        'total_reservations': total_reservations,
        'pending_reservations': pending_reservations,
        'confirmed_reservations': confirmed_reservations,
        'rejected_reservations': rejected_reservations,
        'bookings': bookings,
        'selected_status': selected_status,
    }

    return render(
        request,
        'management/reservations.html',
        context
    )

@login_required
@user_passes_test(manager_required)

def reservation_detail(request, booking_id):
    booking = Booking.objects.select_related('guest', 'property').get(id=booking_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'confirm':
            booking.status = 'Confirmed'
            booking.save()
            messages.success(request, 'Reservation confirmed successfully.')
            return redirect('reservation_detail', booking_id=booking.id)

        if action == 'reject':
            booking.status = 'Rejected'
            booking.save()
            messages.success(request, 'Reservation rejected.')
            return redirect('reservation_detail', booking_id=booking.id)

    return render(request, 'management/reservation_detail.html', {'booking': booking})

@login_required
@user_passes_test(manager_required)
def confirm_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    booking.status = 'Confirmed'
    booking.save()
    messages.success(request, 'Reservation confirmed successfully.')
    return redirect('reservation_detail', booking_id=booking.id)

@login_required
@user_passes_test(manager_required)
def reject_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    booking.status = 'Rejected'
    booking.save()
    messages.success(request, 'Reservation rejected successfully.')
    return redirect('reservation_detail', booking_id=booking.id)

@login_required
@user_passes_test(manager_required)
def management_guests(request):
    guests = Guest.objects.annotate(
        booking_count=Count('bookings')
    ).order_by('-id')

    total_guests = Guest.objects.count()
    individual_guests = Guest.objects.filter(guest_type='individual').count()
    group_guests = Guest.objects.exclude(guest_type='individual').count()

    context = {
        'guests': guests,
        'total_guests': total_guests,
        'individual_guests': individual_guests,
        'group_guests': group_guests,
    }

    return render(request, 'management/guests.html', context)
@login_required
@user_passes_test(manager_required)
def management_experiences(request):
    default_experiences = [
        {
            'name': 'Poolside',
            'description': 'Relax beside the pool and enjoy peaceful moments surrounded by the beauty of Ecovana.',
            'price': 1200,
        },
        {
            'name': 'Dining',
            'description': 'Experience delicious cuisine prepared with care in a beautiful and peaceful resort setting.',
            'price': 1800,
        },
        {
            'name': 'Wellness',
            'description': 'Reconnect with yourself through calming wellness moments surrounded by nature and tranquillity.',
            'price': 1300,
        },
        {
            'name': 'Nature Trails',
            'description': 'Discover scenic trails, lush greenery and the untouched natural beauty surrounding Ecovana.',
            'price': 1000,
        },
        {
            'name': 'Fitness',
            'description': 'Stay active with energising workouts while enjoying the calm surroundings of the resort.',
            'price': 800,
        },
    ]

    for item in default_experiences:
        Experience.objects.get_or_create(
            name=item['name'],
            defaults={
                'description': item['description'],
                'price': item['price'],
                'is_available': True,
            }
        )

    experiences = Experience.objects.all().order_by('id')

    return render(
        request,
        'management/experiences.html',
        {
            'experiences': experiences,
            'total_experiences': experiences.count(),
        }
    )

@login_required
@user_passes_test(manager_required)
def edit_experience(request, experience_name):
    name_map = {
        'poolside': 'Poolside',
        'dining': 'Dining',
        'wellness': 'Wellness',
        'nature-trails': 'Nature Trails',
        'fitness': 'Fitness',
    }

    actual_name = name_map.get(experience_name)

    if not actual_name:
        messages.error(request, 'Experience not found.')
        return redirect('management_experiences')

    experience = get_object_or_404(Experience, name=actual_name)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price')
        image = request.FILES.get('image')
        is_available = request.POST.get('is_available') == 'on'

        if not all([name, description, price]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('edit_experience', experience_name=experience_name)

        try:
            price = float(price)
        except (ValueError, TypeError):
            messages.error(request, 'Please enter a valid price.')
            return redirect('edit_experience', experience_name=experience_name)

        if price < 0:
            messages.error(request, 'Price cannot be negative.')
            return redirect('edit_experience', experience_name=experience_name)

        experience.name = name
        experience.description = description
        experience.price = price
        experience.is_available = is_available

        if image:
            experience.image = image

        experience.save()

        messages.success(request, f'{name} has been updated successfully.')
        return redirect('management_experiences')

    return render(
        request,
        'management/edit_experience.html',
        {'experience': experience}
    )

from django.db import models


class Property(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to='properties/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Experience(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='experiences/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Guest(models.Model):
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(default=18)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    guest_type = models.CharField(max_length=20,default='individual')

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Rejected', 'Rejected'),
    ]

    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='bookings')
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField()
    special_request = models.TextField(blank=True)
    guest_image = models.ImageField(upload_to='guest_images/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.guest.name} - {self.property.name}"

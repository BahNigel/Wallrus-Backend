from django.db import models

# Create your models here.

SECTION_NAME_CHOICES = [
    ('understand_wallrus_business_ecosystem', 'Understand The Wallrus Business Ecosystem'),
    ('artists_agreements','Artist’s Agreements'),
    ('uploading_managing_designs','Uploading and Managing your Designs'),
    ('understanding_media_art_working','Understanding the Media & Art working'),
    ('footer', 'Footer'),
    ('seller_agreement', 'Seller agreement'),
    ('return_exchange', 'Return and exchange'),
    ('privacy_policy', 'Privacy policy'),
    ('terms_of_use', 'Terms of use'),
    ('data_deletion', 'User data deletion instruction'),
]

class Section(models.Model):
    name = models.CharField(max_length=50, choices=SECTION_NAME_CHOICES, unique=True)
    header = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

class Content(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    sequence_number = models.IntegerField()
    heading = models.CharField(max_length=200, null=True, blank=True)
    text = models.TextField()

    def __str__(self):
        return f"{self.section} - {self.sequence_number} - {self.heading if self.heading is not None else ''}"

ADMIN_CONTROL_CHOICES = [
    ('admin_mail', 'Admin notification email'),
    ('main_email_password', 'Main email Password'),
]

class AdminControl(models.Model):
    name = models.CharField(max_length=50, choices=ADMIN_CONTROL_CHOICES, unique=True)
    value = models.CharField(max_length=300)
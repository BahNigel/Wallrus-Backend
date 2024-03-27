from django.db import models
from django.utils.text import slugify

from users.models import CustomUser
from product.models import Application, Product

import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from backend import settings

class DesignTag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    label = models.CharField(max_length=255)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [models.Index(fields=['name'])]


class Design(models.Model):
    artist = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    applications = models.ManyToManyField(Application)
    tags = models.ManyToManyField(DesignTag)
    is_customizable = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return f'{self.pk}: {self.name} uploaded by {self.artist.email}'

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.artist.type == 2:
                self.is_public = False

        if not self.slug:
            self.slug = slugify(self.name + ' by ' + self.get_artist_name())
        
        if self.is_rejected == True and self.is_approved == False:
            print("----------------")
            colorways = Colorway.objects.filter(design__id = self.id).delete()
            print(colorways)
            colorways = Colorway.objects.filter(design__id = self.id).delete()
            print(colorways)
            design_rejected_sendMail(self)
        elif self.is_rejected == False and self.is_approved == True:
            design_approved_sendMail(self)
            
        super().save(*args, **kwargs)
        # super().save(*args, **kwargs)

    def get_artist_name(self):
        return self.artist.first_name + ' ' + self.artist.last_name

    class Meta:
        indexes = [models.Index(fields=['slug'])]

def design_rejected_sendMail(self):
    to = self.artist.email

    msg = EmailMessage()

    body = f"""
    Dear {self.artist.first_name},

    Your design, {self.name} got rejected.

    Design name: {self.name}

    Thanks,
    The Wallrus Team
    """

    # Set email body
    msg = MIMEText(body)

    # Set email Subject, From, To
    msg['Subject'] = f'{self.name} - Your design got rejected'
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = to

    # Setup server and send mail
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    server.sendmail(settings.EMAIL_HOST_USER, to, msg.as_string())
    server.quit()


def design_approved_sendMail(self):
    to = self.artist.email

    msg = EmailMessage()

    body = f"""
    Dear {self.artist.first_name},

    Your design, {self.name} got approved.

    Design name: {self.name}

    Thanks,
    The Wallrus Team
    """

    # Set email body
    msg = MIMEText(body)

    # Set email Subject, From, To
    msg['Subject'] = f'{self.name} - Your design got rejected'
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = to

    # Setup server and send mail
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    server.sendmail(settings.EMAIL_HOST_USER, to, msg.as_string())
    server.quit()

def image_upload_to(instance, filename):
    return f'designs/{instance.collection.artist.id}/{instance.collection.id}/{filename}'


class Colorway(models.Model):
    design = models.ForeignKey(Design, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    image_url = models.URLField()
    color_tags = models.ManyToManyField(
        DesignTag, limit_choices_to={'label': 'Color'}, null=True, blank=True)

    def __str__(self):
        return f'{self.name}'

class Customization(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=10)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  
    width = models.IntegerField()
    height = models.IntegerField()
    unit = models.CharField(max_length=4)
    remarks = models.TextField()
    image1 = models.ImageField(upload_to='custom_designs/')
    image2 = models.ImageField(upload_to='custom_designs/', null=True, blank=True)
    image3 = models.ImageField(upload_to='custom_designs/', null=True, blank=True)
    image4 = models.ImageField(upload_to='custom_designs/', null=True, blank=True)


class UploadOwnDesign(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=10)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  
    width = models.IntegerField()
    height = models.IntegerField()
    unit = models.CharField(max_length=4)
    remarks = models.TextField()
    link = models.URLField()
    price = models.IntegerField()
from django.db import models
from users.models import CustomUser
from invite.util import generate_ref_code

# Below attributes added for invite friend - Refferal System
class Invite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=12)
    referred_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="reffered_by", null=True, blank=True)

    def __str__(self):
        return f"{self.user} referred by {self.referred_by}"

    def save(self, *args, **kwargs):
       self.referral_code = generate_ref_code()
       super().save(*args, **kwargs) # Call the real save() method
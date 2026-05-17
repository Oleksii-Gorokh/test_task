from django.db import models
from django.contrib.auth.models import User

ROLE_CHOICES = [
    ('user', 'Користувач'),
    ('admin', 'Адміністратор'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Профіль користувача'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} ({self.role})"

    def is_admin(self):
        return self.role == 'admin'

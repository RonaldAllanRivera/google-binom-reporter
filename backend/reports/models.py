from django.db import models

class GoogleAccount(models.Model):
    user_email = models.EmailField()
    google_ads_customer_id = models.CharField(max_length=20, blank=True, null=True)
    refresh_token = models.TextField()
    access_token = models.TextField(blank=True, null=True)
    token_expiry = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Google OAuth Account"
        verbose_name_plural = "Google OAuth Accounts"

    def __str__(self):
        return self.user_email
    


class ReportRecord(models.Model):
    REPORT_TYPE_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )

    account_name = models.CharField(max_length=255)
    campaign_name = models.CharField(max_length=255)
    total_spend = models.DecimalField(max_digits=12, decimal_places=2)
    revenue = models.DecimalField(max_digits=12, decimal_places=2)
    pl = models.DecimalField(max_digits=12, decimal_places=2)
    roi = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    sales = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    report_type = models.CharField(max_length=10, choices=REPORT_TYPE_CHOICES, default='monthly')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.report_type} - {self.account_name} ({self.start_date} to {self.end_date})"


from django.db import models
from django.contrib.auth.models import User

class Portfolio(models.Model):
    investor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    ticker = models.CharField(max_length=16)
    quantity = models.PositiveIntegerField()
    avg_buy_price = models.FloatField(default=0)
    
    def __str__(self):
        return f"{self.investor.username} - {self.ticker} ({self.quantity})"

class Recommendation(models.Model):
    analyst = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    investor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommended_to')
    ticker = models.CharField(max_length=16)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.analyst.username} → {self.investor.username}: {self.ticker}"

class AnalystInvestorAssignment(models.Model):
    analyst = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_investors')
    investor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_analyst')
    
    def __str__(self):
        return f"{self.analyst.username} ↔ {self.investor.username}"

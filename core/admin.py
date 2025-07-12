from django.contrib import admin
from .models import Portfolio, Recommendation, AnalystInvestorAssignment

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('investor', 'ticker', 'quantity', 'avg_buy_price')
    search_fields = ('investor__username', 'ticker')

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('analyst', 'investor', 'ticker', 'created_at')
    search_fields = ('analyst__username', 'investor__username', 'ticker')
    list_filter = ('analyst', 'investor')

@admin.register(AnalystInvestorAssignment)
class AnalystInvestorAssignmentAdmin(admin.ModelAdmin):
    list_display = ('analyst', 'investor')
    search_fields = ('analyst__username', 'investor__username')
    list_filter = ('analyst', 'investor')

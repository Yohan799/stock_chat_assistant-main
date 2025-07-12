from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout as auth_logout
from .forms import SignUpForm

# Sign up view

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']
            group, created = Group.objects.get_or_create(name=role.capitalize())
            user.groups.add(group)
            login(request, user)
            return redirect('dashboard_redirect')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

# Login redirect view
@login_required
def dashboard_redirect(request):
    if request.user.groups.filter(name='Analyst').exists():
        return redirect('analyst_dashboard')
    elif request.user.groups.filter(name='Investor').exists():
        return redirect('investor_dashboard')
    return redirect('login')

# Analyst dashboard
from django.forms import ModelForm
from .models import Portfolio, Recommendation, AnalystInvestorAssignment

class RecommendationForm(ModelForm):
    class Meta:
        model = Recommendation
        fields = ['ticker', 'note']
        labels = {'ticker': 'Stock Ticker', 'note': 'Recommendation Note'}

@login_required
def analyst_dashboard(request):
    analyst = request.user
    assignments = AnalystInvestorAssignment.objects.filter(analyst=analyst)
    investors = [a.investor for a in assignments]
    investor_infos = []
    if request.method == 'POST':
        rec_messages = {}
    else:
        rec_messages = None
    for inv in investors:
        portfolio = Portfolio.objects.filter(investor=inv)
        rec_form = RecommendationForm(request.POST or None, prefix=f'rec_{inv.id}')
        recs = Recommendation.objects.filter(analyst=analyst, investor=inv)
        rec_message = None
        if request.method == 'POST':
            form = RecommendationForm(request.POST, prefix=f'rec_{inv.id}')
            if form.is_valid():
                rec = form.save(commit=False)
                rec.analyst = analyst
                rec.investor = inv
                rec.save()
                rec_message = f"Recommendation for {inv.username} added."
                rec_form = RecommendationForm(prefix=f'rec_{inv.id}')  # Reset form
        investor_infos.append({
            'investor': inv,
            'portfolio': portfolio,
            'rec_form': rec_form,
            'rec_message': rec_message,
            'recommendations': recs,
        })
    context = {
        'investor_infos': investor_infos,
    }
    return render(request, 'analyst_dashboard.html', context)

# Investor dashboard
from .models import Portfolio, Recommendation, AnalystInvestorAssignment
from django import forms

class BuyStockForm(forms.Form):
    ticker = forms.CharField(label='Stock Ticker', max_length=16)
    quantity = forms.IntegerField(label='Quantity', min_value=1)
    price = forms.FloatField(label='Buy Price', min_value=0)

@login_required
def investor_dashboard(request):
    user = request.user
    portfolio = Portfolio.objects.filter(investor=user)
    assignment = AnalystInvestorAssignment.objects.filter(investor=user).first()
    analyst = assignment.analyst if assignment else None
    recommendations = Recommendation.objects.filter(investor=user, analyst=analyst) if analyst else []
    buy_form = BuyStockForm(request.POST or None)
    buy_message = None
    if request.method == 'POST' and 'buy_stock' in request.POST:
        if buy_form.is_valid():
            ticker = buy_form.cleaned_data['ticker'].upper()
            quantity = buy_form.cleaned_data['quantity']
            price = buy_form.cleaned_data['price']
            stock, created = Portfolio.objects.get_or_create(
                investor=user,
                ticker=ticker,
                defaults={'quantity': quantity, 'avg_buy_price': price}
            )
            if not created:
                # Weighted average price calculation
                total_cost = stock.avg_buy_price * stock.quantity + price * quantity
                stock.quantity += quantity
                stock.avg_buy_price = total_cost / stock.quantity
                stock.save()
            buy_message = f"Bought {quantity} shares of {ticker} at {price} each."
            buy_form = BuyStockForm()  # Reset form
    context = {
        'portfolio': portfolio,
        'analyst': analyst,
        'recommendations': recommendations,
        'buy_form': buy_form,
        'buy_message': buy_message,
    }
    return render(request, 'investor_dashboard.html', context)

# Logout view
def logout_view(request):
    auth_logout(request)
    return redirect('login')

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse
from .chat_utils import fetch_and_plot_stock, get_chat_advice

@login_required
@csrf_exempt
def chat_api(request):
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []
    chat_history = request.session['chat_history']
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        plot_url = None
        advice = ""
        ticker = None
        # Try to extract ticker: first ALL UPPERCASE word, 2-10 letters
        words = message.split()
        for word in words:
            if word.isalpha() and word.isupper() and 2 <= len(word) <= 10:
                ticker = word
                break
        if ticker:
            data, plot_url = fetch_and_plot_stock(ticker)
            if data is not None:
                advice = get_chat_advice(message, data, ticker, role='analyst' if request.user.groups.filter(name='Analyst').exists() else 'investor')
            else:
                advice = f"Could not fetch data for ticker: {ticker}."
        else:
            advice = "Please include a valid stock ticker (e.g. AAPL, ADANIENT) in your question."
        chat_history.append({'sender': request.user.username, 'text': message, 'plot_url': None})
        chat_history.append({'sender': 'Assistant', 'text': advice, 'plot_url': plot_url})
        request.session['chat_history'] = chat_history
    if request.headers.get('Hx-Request') == 'true':
        return render(request, 'chat_history.html', {'chat_history': chat_history})
    return render(request, 'chat_box.html', {'chat_history': chat_history})

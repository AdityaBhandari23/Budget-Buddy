from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse

import datetime

from django.db.models import Sum
# Create your views here.


def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except UserPreference.DoesNotExist:
        currency='AED'
            
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'income/index.html', context)


@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/add_income.html', context)

        UserIncome.objects.create(owner=request.user, amount=amount, date=date,
                                  source=source, description=description)
        messages.success(request, 'Record saved successfully')

        return redirect('income')


@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/edit_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/edit_income.html', context)
        income.amount = amount
        income. date = date
        income.source = source
        income.description = description

        income.save()
        messages.success(request, 'Record updated  successfully')

        return redirect('income')


def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'record removed')
    return redirect('income')




def income_source_summary(request):
    todays_date=datetime.date.today()
    six_months_ago=todays_date - datetime.timedelta(days=30*6)
    income=UserIncome.objects.filter(owner=request.user,
        date__gte=six_months_ago, date__lte=todays_date
    )
    finalrep={}

    def get_source(income):
        return income.source

    category_list=list(set(map(get_source,income)))

    def get_income_source_amount(source):
        amount=0
        filtered_by_source=income.filter(source=source)

        for item in filtered_by_source:
            amount += item.amount
        return amount

    for x in income:
        for y in category_list:
            finalrep[y]=get_income_source_amount(y)

    return JsonResponse({'income_source_data':finalrep},safe=False)


def top_sources_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    incomes = UserIncome.objects.filter(
        owner=request.user,
        date__gte=six_months_ago, date__lte=todays_date
    )
    source_data = {}

    def get_source(income):
        return income.source

    category_list = list(set(map(get_source, incomes)))

    def get_income_source_amount(source):
        amount = 0
        filtered_by_source = incomes.filter(source=source)

        for item in filtered_by_source:
            amount += item.amount
        return amount

    for x in category_list:
        source_data[x] = get_income_source_amount(x)

    sorted_source_data = dict(sorted(source_data.items(), key=lambda item: item[1], reverse=True))
    top_sources = list(sorted_source_data.keys())[:5]
    top_amounts = list(sorted_source_data.values())[:5]

    return JsonResponse({'top_sources': top_sources, 'top_amounts': top_amounts})

def total_income_over_time(request):
    today = datetime.date.today()
    months = []
    total_incomes = []

    for i in range(12):
        month = today.replace(day=1) - datetime.timedelta(days=i*30)
        months.append(month.strftime("%b %y"))
        total_incomes.append(UserIncome.objects.filter(date__year=month.year, date__month=month.month).aggregate(total=Sum('amount'))['total'] or 0)

    return JsonResponse({'months': months, 'total_incomes': total_incomes})




def get_current_monthly_income(request):
    current_date = datetime.date.today()
    current_month = current_date.month
    current_year = current_date.year

    incomes = UserIncome.objects.filter(owner=request.user, date__year=current_year, date__month=current_month)
    monthly_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
    return monthly_income

def get_current_annual_income(request):
    current_date = datetime.date.today()
    current_year = current_date.year

    incomes = UserIncome.objects.filter(owner=request.user, date__year=current_year)
    annual_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
    return annual_income

def income_stats_view(request):
    monthly_income = get_current_monthly_income(request)
    annual_income = get_current_annual_income(request)
    stats_data = {
        'monthly_income': monthly_income,
        'annual_income': annual_income,
    }
    return render(request, 'income/stats.html', stats_data)

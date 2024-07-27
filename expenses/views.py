from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Category,Expense
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from userpreferences.models import UserPreference
import datetime

from django.db.models import Sum
# Create your views here.

def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)

@login_required(login_url='/authentication/login')
def index(request):
    categories=Category.objects.all()
    expenses=Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 2)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number) 
      
    try:   
        currency=UserPreference.objects.get(user=request.user).currency
    except UserPreference.DoesNotExist:
        currency='AED'    
    
    
    
    context={
        'expenses':expenses,
        'page_obj': page_obj,
        'currency':currency,

    }
    return render(request,'expenses/index.html',context)

def add_expense(request):
    categories=Category.objects.all()
    context={
        'categories':categories,
        'values':request.POST
    }
    
    if request.method == 'GET':
        return render(request,'expenses/add_expense.html',context) 

    if request.method=="POST":
        amount=request.POST['amount']
        
        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', context)        
        
        description=request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']
                
        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/add_expense.html', context)               
        
        Expense.objects.create(owner=request.user,amount=amount,description=description,date=date,category=category)
        messages.success(request,"Expense saved Successfully")
        
        return redirect('expenses')
 
def expense_edit(request,id):
     expense=Expense.objects.get(pk=id)
     categories=Category.objects.all()
     context={
         'expense':expense,
         'values':expense,
         'categories':categories
     }
     if request.method=='GET':
         return render(request,'expenses/edit-expense.html',context)

     if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit-expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense. date = date
        expense.category = category
        expense.description = description

        expense.save()
        messages.success(request, 'Expense updated  successfully')

        return redirect('expenses')     
    
def delete_expense(request,id):
    expense=Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense Removed')    
    return redirect('expenses')



def expense_category_summary(request):
    todays_date=datetime.date.today()
    six_months_ago=todays_date - datetime.timedelta(days=30*6)
    expenses=Expense.objects.filter(owner=request.user,
        date__gte=six_months_ago, date__lte=todays_date
    )
    finalrep={}
    
    def get_category(expense):
        return expense.category
    
    category_list=list(set(map(get_category,expenses)))
    
    def get_expense_category_amount(category):
        amount=0
        filtered_by_category=expenses.filter(category=category)
        
        for item in filtered_by_category:
            amount += item.amount
        return amount
    
    for x in expenses:
        for y in category_list:
            finalrep[y]=get_expense_category_amount(y)
    
    return JsonResponse({'expense_category_data':finalrep},safe=False)



def top_expenses_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    expenses = Expense.objects.filter(
        owner=request.user,
        date__gte=six_months_ago, date__lte=todays_date
    )
    category_data = {}

    def get_category(expense):
        return expense.category

    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in category_list:
        category_data[x] = get_expense_category_amount(x)

    sorted_category_data = dict(sorted(category_data.items(), key=lambda item: item[1], reverse=True))
    top_category = list(sorted_category_data.keys())[:5]
    top_amounts = list(sorted_category_data.values())[:5]

    return JsonResponse({'top_category': top_category, 'top_amounts': top_amounts})


def total_expense_over_time(request):
    today = datetime.date.today()
    months = []
    total_expenses = []

    for i in range(12):
        month = today.replace(day=1) - datetime.timedelta(days=i*30)
        months.append(month.strftime("%b %y"))
        total_expenses.append(Expense.objects.filter(date__year=month.year, date__month=month.month).aggregate(total=Sum('amount'))['total'] or 0)

    return JsonResponse({'months': months, 'total_expenses': total_expenses})


def get_current_monthly_expense(request):
    current_date = datetime.date.today()
    current_month = current_date.month
    current_year = current_date.year

    expenses = Expense.objects.filter(owner=request.user, date__year=current_year, date__month=current_month)
    monthly_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    return monthly_expense

def get_current_annual_expense(request):
    current_date = datetime.date.today()
    current_year = current_date.year

    expenses = Expense.objects.filter(owner=request.user, date__year=current_year)
    annual_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    return annual_expense

def stats_view(request):
    monthly_expense = get_current_monthly_expense(request)
    annual_expense = get_current_annual_expense(request)
    stats_data = {
        'monthly_expense': monthly_expense,
        'annual_expense': annual_expense,
    }
    return render(request, 'expenses/stats.html', stats_data)
















# from django.shortcuts import render,redirect
# from django.contrib.auth.decorators import login_required
# from .models import Category,Expense
# from django.contrib import messages
# from django.contrib.auth.models import User
# from django.core.paginator import Paginator
# import json
# from django.http import JsonResponse
# from userpreferences.models import UserPreference
# import datetime

# # Create your views here.

# def search_expenses(request):
#     if request.method == 'POST':
#         search_str = json.loads(request.body).get('searchText')
#         expenses = Expense.objects.filter(
#             amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
#             date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
#             description__icontains=search_str, owner=request.user) | Expense.objects.filter(
#             category__icontains=search_str, owner=request.user)
#         data = expenses.values()
#         return JsonResponse(list(data), safe=False)

# @login_required(login_url='/authentication/login')
# def index(request):
#     categories=Category.objects.all()
#     expenses=Expense.objects.filter(owner=request.user)
#     paginator = Paginator(expenses, 2)
#     page_number = request.GET.get('page')
#     page_obj = Paginator.get_page(paginator, page_number) 
      
#     try:   
#         currency=UserPreference.objects.get(user=request.user).currency
#     except UserPreference.DoesNotExist:
#         currency='AED'    
    
    
    
#     context={
#         'expenses':expenses,
#         'page_obj': page_obj,
#         'currency':currency,

#     }
#     return render(request,'expenses/index.html',context)

# def add_expense(request):
#     categories=Category.objects.all()
#     context={
#         'categories':categories,
#         'values':request.POST
#     }
    
#     if request.method == 'GET':
#         return render(request,'expenses/add_expense.html',context) 

#     if request.method=="POST":
#         amount=request.POST['amount']
        
#         if not amount:
#             messages.error(request, 'Amount is required')
#             return render(request, 'expenses/add_expense.html', context)        
        
#         description=request.POST['description']
#         date = request.POST['expense_date']
#         category = request.POST['category']
                
#         if not description:
#             messages.error(request, 'Description is required')
#             return render(request, 'expenses/add_expense.html', context)               
        
#         Expense.objects.create(owner=request.user,amount=amount,description=description,date=date,category=category)
#         messages.success(request,"Expense saved Successfully")
        
#         return redirect('expenses')
 
# def expense_edit(request,id):
#      expense=Expense.objects.get(pk=id)
#      categories=Category.objects.all()
#      context={
#          'expense':expense,
#          'values':expense,
#          'categories':categories
#      }
#      if request.method=='GET':
#          return render(request,'expenses/edit-expense.html',context)

#      if request.method == 'POST':
#         amount = request.POST['amount']

#         if not amount:
#             messages.error(request, 'Amount is required')
#             return render(request, 'expenses/edit-expense.html', context)
#         description = request.POST['description']
#         date = request.POST['expense_date']
#         category = request.POST['category']

#         if not description:
#             messages.error(request, 'description is required')
#             return render(request, 'expenses/edit-expense.html', context)

#         expense.owner = request.user
#         expense.amount = amount
#         expense. date = date
#         expense.category = category
#         expense.description = description

#         expense.save()
#         messages.success(request, 'Expense updated  successfully')

#         return redirect('expenses')     
    
# def delete_expense(request,id):
#     expense=Expense.objects.get(pk=id)
#     expense.delete()
#     messages.success(request, 'Expense Removed')    
#     return redirect('expenses')

# def expense_category_summary(request):
#     todays_date=datetime.date.today()
#     six_months_ago=todays_date - datetime.timedelta(days=30*6)
#     expenses=Expense.objects.filter(owner=request.user,
#         date__gte=six_months_ago, date__lte=todays_date
#     )
#     finalrep={}
    
#     def get_category(expense):
#         return expense.category
    
#     category_list=list(set(map(get_category,expenses)))
    
#     def get_expense_category_amount(category):
#         amount=0
#         filtered_by_category=expenses.filter(category=category)
        
#         for item in filtered_by_category:
#             amount += item.amount
#         return amount
    
#     for x in expenses:
#         for y in category_list:
#             finalrep[y]=get_expense_category_amount(y)
    
#     return JsonResponse({'expense_category_data':finalrep},safe=False)

# def stats_view(request):
#     return render(request, 'expenses/stats.html')
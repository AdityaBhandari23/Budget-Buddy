from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Category,Expense
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator


# Create your views here.

@login_required(login_url='/authentication/login')
def index(request):
    categories=Category.objects.all()
    expenses=Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 2)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)    
    context={
        'expenses':expenses,
        'page_obj': page_obj,

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
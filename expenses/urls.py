from django.urls import path
from .import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index,name="expenses"),
    path('add-expense',views.add_expense,name='add-expenses'),
    path('edit-expense/<int:id>',views.expense_edit,name='expense-edit'),
    path('expense-delete/<int:id>',views.delete_expense,name='expense-delete'),
    path('search-expenses',csrf_exempt(views.search_expenses),name='search-expenses'),
    
    path('expense_category_summary',views.expense_category_summary,name='expense_category_summary'),
    
    path('top_expenses_category_summary',views.top_expenses_category_summary,name='top_expenses_category_summary'),
    
    path('total_expense_over_time',views.total_expense_over_time,name='total_expense_over_time'),
    
    path('stats',views.stats_view,name="stats")
   
]

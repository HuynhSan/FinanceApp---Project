from django.urls import path
from tracker import views



urlpatterns = [
    path("", views.index, name='index'),
    path("transactions/", views.transaction_list, name = 'transaction-list'),
    path("dashboard/", views.dashboard_view, name = 'dashboard'),
    path("transactions/charts", views.transaction_charts, name = 'transactions-charts'),
    path("transactions/create/", views.create_transaction, name = 'create-transaction'),
    path("transactions/<int:pk>/update", views.update_transaction, name = 'update-transaction'), # nhung khoa chinh cua giao dich
    path("transactions/<int:pk>/delete", views.delete_transaction, name = 'delete-transaction'), # nhung khoa chinh cua giao dich
    path("get-transactions/", views.get_transactions, name = 'get-transactions'),
    path('transactions/export', views.export, name='export'),
    path('transactions/import', views.import_transactions, name='import'),

    path('categories/', views.category_list, name='category-list'),
    path('categories/create/', views.create_category, name='create-category'),
    path('categories/<int:pk>/update/', views.update_category, name='update-category'), # nhung khoa chinh cua danh muc
    path('categories/<int:pk>/delete/', views.delete_category, name='delete-category'), # nhung khoa chinh cua danh muc
]

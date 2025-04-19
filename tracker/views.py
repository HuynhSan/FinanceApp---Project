from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from tracker.models import Transaction, Category
from tracker.filters import TransactionFilter
from django.db.models import Sum
from django.core.paginator import Paginator
from django.conf import settings
from tracker.forms import TransactionForm, CategoryForm
from django_htmx.http import retarget
from django.views.decorators.http import require_http_methods
from tracker.charting import plot_income_expenses_bar_chart, plot_category_pie_chart, plot_income_expense_line_chart,  plot_monthly_comparison_line_chart
from tracker.resources import TransactionResource
from django.http import HttpResponse
import time
from datetime import datetime
from tablib import Dataset
from django.db.models import Q
from django.contrib.auth import logout


# Create your views here.
def index(request):
    # logout(request)
    if request.user.is_authenticated:
        return redirect('dashboard')  # đã đăng nhập thì chuyển đến dashboard
    return render(request, 'tracker/index.html')  # chưa đăng nhập thì hiển thị trang index


@login_required
def transaction_list(request):
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category'), user=request.user
    )
    paginator = Paginator(transaction_filter.qs, settings.PAGE_SIZE)
    # transaction_page = paginator.page(1) # default to 1 when this view is triggered

    page_number = request.GET.get('page') or 1
    transaction_page = paginator.get_page(page_number)


    total_income = transaction_filter.qs.get_total_incomes()
    total_expenses = transaction_filter.qs.get_total_expenses()
    context = {
        'transactions': transaction_page,
        'filter': transaction_filter,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_income': total_income - total_expenses
    }

    if request.htmx:
        return render(request, 'tracker/partials/transactions-container.html', context)

    return render(request, 'tracker/transaction_list.html', context)
    

def get_previous_month(year, month):
    """ Trả về tháng trước của tháng hiện tại """
    if month == 1:
        return year - 1, 12  # Tháng 1 thì tháng trước là tháng 12 của năm trước
    return year, month - 1


@login_required
def dashboard_view(request):
    now = datetime.now()
    selected_month = int(request.GET.get('month', now.month))  # Dùng tháng hiện tại nếu không có
    selected_year = int(request.GET.get('year', now.year))  # Dùng năm hiện tại nếu không có
    view_mode = request.GET.get('view_mode', 'latest')

    # Lọc giao dịch cho tháng hiện tại
    transaction_filter = Transaction.objects.filter(
        user=request.user,
        date__month=selected_month,
        date__year=selected_year,
    )
    
    # Lọc giao dịch cho tháng trước
    prev_year, prev_month = get_previous_month(selected_year, selected_month)
    prev_month_filter = Transaction.objects.filter(
        user=request.user,
        date__month=prev_month,
        date__year=prev_year,
    )

    # Tính tổng thu nhập, chi tiêu và các thống kê cho tháng hiện tại
    total_income = transaction_filter.get_total_incomes()
    total_expense = transaction_filter.get_total_expenses()
    total_transactions = transaction_filter.count()
    top_category = transaction_filter.top_expense_category()

    # Chọn dữ liệu theo chế độ xem
    if view_mode == "monthly":
        recent_transactions = transaction_filter.order_by('-date')
    else:
        recent_transactions = transaction_filter.order_by('-date')[:5]

    # Vẽ biểu đồ thu nhập và chi tiêu cho tháng hiện tại
    income_expense_line = plot_income_expense_line_chart(transaction_filter)

    # Vẽ biểu đồ so sánh giữa tháng hiện tại và tháng trước
    comparison_line = plot_monthly_comparison_line_chart(transaction_filter, prev_month_filter, selected_month, prev_month)

    context = {
        'selected_month': selected_month,
        'selected_year': selected_year,
        'total_income': total_income,
        'total_expense': total_expense,
        'total_transactions': total_transactions,
        'recent_transactions': recent_transactions,
        'net_income': total_income - total_expense,
        'top_category': top_category,
        'view_mode': view_mode,
        'income_expense_linechart': income_expense_line.to_html(config={
            'staticPlot': True,
            'displayModeBar': False
        }),
        'comparison_linechart': comparison_line.to_html(config={
            'staticPlot': True,
            'displayModeBar': False
        }),
    }
    return render(request, 'tracker/dashboard.html', context)

@login_required
def category_list(request):
    # Lấy các danh mục mặc định (user=null) hoặc của người dùng hiện tại
    categories = Category.objects.filter(
        Q(user=request.user) | Q(user__isnull=True)
    )

    context = {
        'categories': categories,
    }

    if request.htmx:
        return render(request, 'tracker/partials/category-container.html', context)

    return render(request, 'tracker/category_list.html', context)

@login_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, user=request.user)  # ✅ truyền user
        if form.is_valid():
            form.save()
            context = {
                'message': "Category was added successfully!",
                'message_type': 'success',
                'action': 'add'
            }
            return render(request, 'tracker/partials/category_success.html', context)
        else:
            context = {'form': form}
            response = render(request, 'tracker/partials/create_category.html', context)
            return retarget(response, '#category-block')
    else:
        form = CategoryForm(user=request.user)  # ✅ truyền user cho GET form

    context = {'form': form}
    return render(request, 'tracker/partials/create_category.html', context)


@login_required
@require_http_methods(["DELETE"])
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    # Cấm xoá nếu là danh mục mặc định
    if category.user is None:
        context = {
            'message': "You are not allowed to delete default categories.",
            'message_type': 'error'
        }
        # Trả về 200 để HTMX swap được
        return render(request, 'tracker/partials/category_success.html', context)

    # Cấm xoá nếu không phải danh mục của người dùng
    if category.user != request.user:
        context = {
            'message': "You are not allowed to delete this category.",
            'message_type': 'error'
        }
        return render(request, 'tracker/partials/category_success.html', context)

    # Cấm xoá nếu danh mục đang được dùng trong giao dịch
    if Transaction.objects.filter(category=category).exists():
        context = {
            "message": "Cannot delete category because it is used in transactions.",
            "message_type": "error"
        }
        return render(request, 'tracker/partials/category_success.html', context)

    # Xoá danh mục
    category.delete()

    context = {
        "message": f"Category '{category.name}' was deleted successfully!",
        "message_type": "success",
        "action": "delete"
    }
    return render(request, 'tracker/partials/category_success.html', context)


@login_required
def create_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST or None, user=request.user)  # ✅ truyền user
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            context = {
                'message': "Transaction was added successfully!",
                'message_type': 'success',
                'action': 'add'
                }
            return render(request, 'tracker/partials/transaction_success.html', context)

        else:
            context = {'form': form}
            response =  render(request, 'tracker/partials/create_transaction.html', context)
            return retarget(response, '#transaction-block')

    context = {'form': TransactionForm(user=request.user)}
    return render(request, 'tracker/partials/create_transaction.html', context)


@login_required
def update_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)  # ✅ truyền user
        if form.is_valid():
            transaction = form.save()
            context = {
                'message': "Transaction was updated successfully!",
                'message_type': 'success',
                'action': 'update'
                }
            return render(request, 'tracker/partials/transaction_success.html', context)
        else:
            context = {
                'form': form,
                'transaction': transaction,
            }
            response = render(request, 'tracker/partials/update_transaction.html', context)
            return retarget(response, '#transaction-block')
        
    context = {
        'form': TransactionForm(instance=transaction, user=request.user),
        'transaction': transaction,
    }
    return render(request, 'tracker/partials/update_transaction.html', context)


@login_required
def update_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    # Cấm sửa nếu không phải của người dùng
    if category.user is None:
        context = {
            'message': "You are not allowed to change this category.",
            'message_type': 'error'
        }
        return render(request, 'tracker/partials/category_success.html', context)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category, user=request.user)  # ✅ truyền user
        if form.is_valid():
            form.save()
            context = {
                'message': "Category was updated successfully!",
                'message_type': 'success',
                'action': 'edit'
            }
            return render(request, 'tracker/partials/category_success.html', context)
        else:
            context = {'form': form}
            return render(request, 'tracker/partials/update_category.html', context)
    else:
        form = CategoryForm(instance=category, user=request.user)

    context = {'form': form, 'category': category}
    return render(request, 'tracker/partials/update_category.html', context)


@login_required
@require_http_methods(["DELETE"])
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    transaction.delete()
    context = {
        'message': f"Transaction of {transaction.amount} on {transaction.date} was deleted successfully!",
        'message_type': 'success',
        'action': 'delete'
    }
    return render(request, 'tracker/partials/transaction_success.html', context)



@login_required
def get_transactions(request):
    time.sleep(0.5)
    page = request.GET.get('page', 1)  # ?page=2
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category')
    )
    paginator = Paginator(transaction_filter.qs, settings.PAGE_SIZE)
    context = {
        'transactions': paginator.page(page)
    }
    return render(
        request,
        'tracker/partials/transactions-container.html#transaction_list',
        context
    )

@login_required
def transaction_charts(request):
    # Lọc giao dịch của người dùng hiện tại
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category'), user=request.user
    )

    # Các biểu đồ hiện tại
    income_expense_bar = plot_income_expenses_bar_chart(transaction_filter.qs)
    category_income_pie = plot_category_pie_chart(transaction_filter.qs.filter(type='income'))
    category_expense_pie = plot_category_pie_chart(transaction_filter.qs.filter(type='expense'))

    # Thêm biểu đồ đường
    income_expense_line = plot_income_expense_line_chart(transaction_filter.qs)

    context = {
        'filter': transaction_filter,
        'income_expense_barchart': income_expense_bar.to_html(config={
            'staticPlot': True,
            'displayModeBar': False
        }),
        'category_income_pie': category_income_pie.to_html(config={
            'staticPlot': True,
            'displayModeBar': False
        }),
        'category_expense_pie': category_expense_pie.to_html(config={
            'staticPlot': True,
            'displayModeBar': False
        }),
        # Thêm biểu đồ đường vào context
        'income_expense_linechart': income_expense_line.to_html(config={
            'staticPlot': True,
            'displayModeBar': False
        }),
    }

    if request.htmx:
        return render(request, 'tracker/partials/charts-container.html', context)

    return render(request, 'tracker/charts.html', context)




@login_required
def export(request):
    if request.htmx:
        return HttpResponse(headers={'HX-Redirect': request.get_full_path()})
    
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category')
    )

    data = TransactionResource().export(transaction_filter.qs)
    response = HttpResponse(data.csv)
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    return response

@login_required
def import_transactions(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        resource = TransactionResource()
        dataset = Dataset()
        dataset.load(file.read().decode(), format='csv')
        result = resource.import_data(dataset, user=request.user, dry_run=True)

        print("== Dry run errors check ==")
        print("Has errors:", result.has_errors())
        print("Base errors:", result.base_errors)

        for row in result.invalid_rows:
            print(f"Row error: {row.errors}")


        print("Import result:", result.has_errors())

        if not result.has_errors():
            resource.import_data(dataset, user=request.user, dry_run=False)

            context = {
                'message': (
                    f'{resource.created_count} transactions created. '
                    f'{resource.updated_count} transactions updated. '
                    f'{resource.skipped_count} skipped.'
                )
            }
        else:
            context = {
                'message': 'Sorry, some rows have errors. Please check the input file.',
                'errors': [row.errors for row in result.rows if row.errors]
            }

        return render(request, 'tracker/partials/transaction_success.html', context)
    return render(request, 'tracker/partials/import-transaction.html')
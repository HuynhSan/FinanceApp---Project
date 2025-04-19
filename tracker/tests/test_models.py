import pytest
from tracker.models import Transaction

#  Kiểm thử phương thức get_incomes của queryset, đảm bảo chỉ trả về các giao dịch có type = 'income'
@pytest.mark.django_db
def test_queryset_get_income_method(transactions_test):
    qs = Transaction.objects.get_incomes()
    assert qs.count() > 0  # Đảm bảo có ít nhất 1 giao dịch thu nhập
    assert all(
        [transaction.type == 'income' for transaction in qs]  # Kiểm tra tất cả giao dịch đều có type là 'income'
    )

#  Kiểm thử phương thức get_expenses, đảm bảo chỉ trả về giao dịch chi tiêu (type = 'expense')
@pytest.mark.django_db
def test_queryset_get_expenses_method(transactions_test):
    qs = Transaction.objects.get_expenses()
    assert qs.count() > 0  # Đảm bảo có ít nhất 1 giao dịch chi tiêu
    assert all(
        [transaction.type == 'expense' for transaction in qs]  # Kiểm tra tất cả giao dịch đều có type là 'expense'
    )

#  Kiểm thử phương thức get_total_expenses, đảm bảo tổng chi tiêu khớp với dữ liệu đã tạo
@pytest.mark.django_db
def test_queryset_get_total_expenses_method(transactions_test):
    total_expenses = Transaction.objects.get_total_expenses()
    assert total_expenses == sum(
        t.amount for t in transactions_test if t.type == 'expense'  # Tính tổng amount của giao dịch có type 'expense'
    )

#  Kiểm thử phương thức get_total_incomes, đảm bảo tổng thu nhập khớp với dữ liệu đã tạo
@pytest.mark.django_db
def test_queryset_get_total_incomes_method(transactions_test):
    total_incomes = Transaction.objects.get_total_incomes()
    assert total_incomes == sum(
        t.amount for t in transactions_test if t.type == 'income'  # Tính tổng amount của giao dịch có type 'income'
    )

#  Kiểm thử phương thức get_recent_transactions, đảm bảo trả về 5 giao dịch mới nhất (sắp xếp theo ngày giảm dần)
@pytest.mark.django_db
def test_queryset_get_recent_transactions_method(transactions_test):
    qs = Transaction.objects.get_recent_transactions()  # qs là một QuerySet gồm 5 giao dịch gần nhất
    expected = sorted(transactions_test, key=lambda x: x.date, reverse=True)[:5]  # Tạo danh sách 5 giao dịch mới nhất từ fixture
    assert list(qs) == expected  # So sánh dữ liệu mong đợi với kết quả từ phương thức

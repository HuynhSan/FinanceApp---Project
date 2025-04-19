import pytest 
from django.urls import reverse
from datetime import datetime, timedelta
from tracker.models import Category, Transaction
from pytest_django.asserts import assertTemplateUsed

@pytest.mark.django_db
def test_total_values_appear_on_list_page(user_transactions, client):
    user = user_transactions[0].user  # Lấy user từ danh sách giao dịch được tạo sẵn bằng fixture
    client.force_login(user)  # Đăng nhập user đó để có quyền truy cập các trang yêu cầu xác thực

    # Tính tổng thu, tổng chi, thu nhập ròng
    income_total = sum(t.amount for t in user_transactions if t.type == 'income')
    expense_total = sum(t.amount for t in user_transactions if t.type == 'expense') 
    net_income = income_total - expense_total

    # Gửi yêu cầu GET đến view tên là 'transaction-list' để lấy các trường trong context, reverse('transaction-list') sẽ tạo ra URL tương ứng với tên route 'transaction-list'
    response = client.get(reverse('transaction-list'))

    # Kiểm tra xem giá trị trong context trả về có đúng như đã tính không
    assert response.context['total_income'] == income_total
    assert response.context['total_expenses'] == expense_total
    assert response.context['net_income'] == net_income


@pytest.mark.django_db
def test_transaction_type_filter(user_transactions, client):
    user = user_transactions[0].user  # Lấy user từ danh sách giao dịch được tạo sẵn bằng fixture
    client.force_login(user)  # Đăng nhập user đó để có quyền truy cập các trang yêu cầu xác thực

    # Giả sử khi chọn type = income
    GET_params = {'transaction_type':'income'}
    response = client.get(reverse('transaction-list'), GET_params)

    qs = response.context['filter'].qs  # .qs: lấy queryset đã được lọc

    for transaction in qs:
        assert transaction.type == 'income'


    # Giả sử khi chọn type = expense
    GET_params = {'transaction_type':'expense'} #transaction_type là biến lọc
    response = client.get(reverse('transaction-list'), GET_params)

    qs = response.context['filter'].qs  # .qs: lấy queryset đã được lọc

    for transaction in qs:
        assert transaction.type == 'expense'

@pytest.mark.django_db
def test_start_end_date_filter(user_transactions, client):
    user = user_transactions[0].user
    client.force_login(user)

    start_date_cutoff = datetime.now().date()
    GET_params = {'start_date': start_date_cutoff}
    response = client.get(reverse('transaction-list'), GET_params)

    qs = response.context['filter'].qs

    for transaction in qs:
        assert transaction.date >= start_date_cutoff


    end_date_cutoff = datetime.now().date()
    GET_params = {'end_date': end_date_cutoff}
    response = client.get(reverse('transaction-list'), GET_params)

    qs = response.context['filter'].qs

    for transaction in qs:
        assert transaction.date <= end_date_cutoff

@pytest.mark.django_db
def test_category_filter(user_transactions, client):
    user = user_transactions[0].user
    client.force_login(user)

    # Lấy 2 category đầu tiên từ database, chỉ lấy primary key (id)
    category_pks = Category.objects.all()[:2].values_list('pk', flat=True)

    # Tạo tham số GET để lọc theo nhiều category
    GET_params = {'category': category_pks}

    response = client.get(reverse('transaction-list'), GET_params)
    qs = response.context['filter'].qs

    # Kiểm tra từng transaction trả về có category nằm trong danh sách đã chọn
    for transaction in qs:
        assert transaction.category.pk in category_pks



@pytest.mark.django_db
def test_add_transaction_request(
    user, 
    transaction_dict_params, 
    client
    ):

    client.force_login(user)
    user_transaction_count = Transaction.objects.filter(user=user).count()

    # send request with transaction data
    headers = {'HTTP_HX-Request': 'true'}
    response = client.post(
        reverse('create-transaction'),
        transaction_dict_params,
        **headers
    )

    # assert the count has increased after the POST request
    assert Transaction.objects.filter(user=user).count() == user_transaction_count + 1

    assertTemplateUsed(response, 'tracker/partials/transaction_success.html')


@pytest.mark.django_db
def test_cannot_add_transaction_with_negative_amount(
    user, 
    transaction_dict_params, 
    client
    ):

    client.force_login(user)
    user_transaction_count = Transaction.objects.filter(user=user).count()

    transaction_dict_params['amount'] = -10
    # send request with transaction data
    response = client.post(
        reverse('create-transaction'),
        transaction_dict_params,
    )

    # assert the count has increased after the POST request
    assert Transaction.objects.filter(user=user).count() == user_transaction_count

    assertTemplateUsed(response, 'tracker/partials/create_transaction.html')
    assert 'HX-Retarget' in response.headers


@pytest.mark.django_db
def test_update_transaction_request(
    user, 
    transaction_dict_params, 
    client
    ):

    client.force_login(user)
    assert Transaction.objects.filter(user=user).count() == 1

    transaction = Transaction.objects.first()

    now = datetime.now().date()
    transaction_dict_params['amount'] = 23
    transaction_dict_params['date'] = now
    client.post(
            reverse('update-transaction', kwargs={'pk': transaction.pk}),
            transaction_dict_params
        )
    
    assert Transaction.objects.filter(user=user).count() == 1
    transaction = Transaction.objects.first()
    assert transaction.amount == 23
    assert transaction.date == now


@pytest.mark.django_db
def test_delete_transaction_request(
    user, 
    transaction_dict_params, 
    client
    ):

    client.force_login(user)
    assert Transaction.objects.filter(user=user).count() == 1
    transaction = Transaction.objects.first()

    client.delete(
        reverse('delete-transaction', kwargs={'pk': transaction.pk})
    )

    assert Transaction.objects.filter(user=user).count() == 0


# Người dùng chưa đăng nhập sẽ thấy trang index
@pytest.mark.django_db
def test_index_view_unauthenticated_user(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "tracker/index.html" in [t.name for t in response.templates]


# Người dùng đã đăng nhập sẽ bị redirect tới dashboard
@pytest.mark.django_db
def test_index_view_authenticated_user_redirect(client, django_user_model):
    user = django_user_model.objects.create_user(username="testuser", password="testpass")
    client.login(username="testuser", password="testpass")

    response = client.get("/")
    assert response.status_code == 302
    assert response.url == "/dashboard/"  # hoặc reverse('dashboard') nếu muốn chắc chắn


# Đăng nhập thành công
@pytest.mark.django_db
def test_login_success(client, django_user_model):
    django_user_model.objects.create_user(username="testuser", password="testpass")
    response = client.post('/accounts/login/', {
        'login': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 302  # redirect sau khi login

# Đăng kí thành công
@pytest.mark.django_db
def test_signup_success(client, django_user_model):
    response = client.post('/accounts/signup/', {
        'username': 'newuser',
        'password1': 'strongpass123',
        'password2': 'strongpass123'
    })
    assert response.status_code == 302
    assert django_user_model.objects.filter(username='newuser').exists()


# Đăng xuất thành công
@pytest.mark.django_db
def test_logout_success1(client, django_user_model):
    # Tạo user và đăng nhập
    user = django_user_model.objects.create_user(username="testuser", password="testpass")
    client.login(username="testuser", password="testpass")

    # Gửi yêu cầu đến trang xác nhận logout
    response = client.get('/accounts/logout/')
    assert response.status_code == 200  # Trang xác nhận logout

    # Gửi yêu cầu xác nhận logout (giả sử là POST hoặc GET tiếp theo)
    response = client.post('/accounts/logout/')  # Hoặc client.get nếu dùng GET
    assert response.status_code == 302  # Redirect sau khi logout
    assert response.url == "/"  # Kiểm tra chuyển hướng về trang index
    assert '_auth_user_id' not in client.session  # Kiểm tra session không còn user
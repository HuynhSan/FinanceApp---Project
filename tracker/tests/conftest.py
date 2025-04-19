import pytest
from tracker.factories import TransactionFactory, UserFactory

#  Fixture tạo 20 giao dịch (Transaction) với user ngẫu nhiên cho mỗi cái
@pytest.fixture
def transactions_test():
    # Sử dụng TransactionFactory để tạo 20 giao dịch
    # Mỗi giao dịch có thể có user khác nhau
    return TransactionFactory.create_batch(20)


#  Fixture tạo 1 user và 20 giao dịch đều thuộc về user đó
@pytest.fixture
def user_transactions():
    # Tạo một user bằng UserFactory
    user = UserFactory()
    
    # Tạo 20 giao dịch và gán tất cả giao dịch này cho user vừa tạo
    return TransactionFactory.create_batch(20, user=user)


# Fixture pytest cho user, dùng để cung cấp một đối tượng người dùng giả lập (fake user)
@pytest.fixture
def user():
    # Trả về một instance của User được tạo từ UserFactory (giả lập 1 user)
    return UserFactory()


# Tạo một fixture pytest cho dữ liệu dictionary đại diện cho một transaction
@pytest.fixture
def transaction_dict_params(user):
    # Tạo một transaction giả (fake transaction) với user vừa tạo ở trên
    transaction = TransactionFactory.create(user=user)

    # Trả về một dictionary chứa các trường chính của transaction, dùng để gửi vào form hoặc API khi test
    return {
        'type': transaction.type,               # Loại giao dịch (thu/chi)
        'category': transaction.category_id,    # ID của danh mục giao dịch
        'date': transaction.date,               # Ngày giao dịch
        'amount': transaction.amount,           # Số tiền giao dịch
    }



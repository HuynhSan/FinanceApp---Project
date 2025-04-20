from datetime import datetime
import factory 
from tracker.models import Category, Transaction, User

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User  # chỉ định model mà factory tạo ra
        django_get_or_create = ('username',) # nếu có username trùng thì dùng lại bản ghi đã có

    # tự động sinh tên giả bằng Faker
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.Sequence(lambda n: 'user%d' % n) # Sinh ra chuỗi user0, user1, user2,... theo thứ tự tăng dần — để đảm bảo username là duy nhất.


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category 
        django_get_or_create = ('name',) 
    
    

    # factory.Iterator() sẽ lặp qua các giá trị được truyền vào, và mỗi lần tạo instance mới, nó sẽ lấy giá trị kế tiếp.
    name = factory.Iterator(
        ['Bills', 'Housing', 'Salary', 'Food', 'Social']
    
    )


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    amount = 5
    date = factory.Faker(
        'date_between',
        start_date=datetime(year=2022, month=1, day=1).date(),
        end_date=datetime.now().date()
    )

    type = factory.Iterator(
        [
            x[0] for x in Transaction.TRANSACTION_TYPE_CHOICES
        ]
    )

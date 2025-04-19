import random
from faker import Faker # thu vien tao du lieu gia dinh
from django.core.management.base import BaseCommand
from tracker.models import User, Transaction, Category


class Command(BaseCommand):
    help = "Generates transactions for testing"

    def handle(self, *args, **options): #ham chinh duoc goi 
        fake = Faker()

        # tao danh muc (co the co)
        categories = [
            "Bills",
            "Food",
            "Clothes",
            "Medical",
            "Housing",
            "Salary",
            "Social",
            "Transport",
            "Vacation",
        ]

        for category in categories:
            Category.objects.get_or_create(name = category) #kiem tra danh muc co ton tai chua (chua co thi tao, co thi bo qua)

        #lay nguoi dung tu co so du lieu
        user = User.objects.filter(username = 'lesan').first()
        if not user:
            user = User.objects.create_superuser(username='lesan', password='12345@12345')

        categories = Category.objects.all()
        types = [x[0] for x in Transaction.TRANSACTION_TYPE_CHOICES] # tra ve income va expense
        for i in range(20):
            Transaction.objects.create(
                category=random.choice(categories),
                user=user,
                amount=random.uniform(1, 2500),
                date=fake.date_between(start_date='-1y', end_date='today'),
                type=random.choice(types),
            )
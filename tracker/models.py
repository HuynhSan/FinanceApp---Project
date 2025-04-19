from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import TransactionQuerySet

class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        constraints = [
            models.UniqueConstraint(fields=['name', 'user'], name='unique_category_per_user')  # Đảm bảo một người dùng không có hai danh mục trùng tên
        ]

    def __str__(self):
        return self.name



# has a CATEGORY (FK)
# is tied to a User (FK)
# has a DATE
class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('income', 'Income'), #income luu trong database, Income hien thi trong form
        ('expense', 'Expense'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete= models.CASCADE)
    type = models.CharField(max_length=7, choices=TRANSACTION_TYPE_CHOICES) # toi da 7 ky tu ( du cho income va expense)
    amount = models.DecimalField(max_digits=10, decimal_places=2) # toi da 10 chu so(phan nguyen va thap phan), co 2 chu so thap phan
    date = models.DateField()

    objects = TransactionQuerySet.as_manager()

    def __str__(self):
        return f"{self.type} of {self.amount} on {self.date} by {self.user}"
    
    class Meta:
        ordering = ['-date']
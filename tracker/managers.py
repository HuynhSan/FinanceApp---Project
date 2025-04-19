from django.db import models

class TransactionQuerySet(models.QuerySet):
    def get_expenses(self):
        return self.filter(type="expense")
    
    def get_incomes(self):
        return self.filter(type="income")
    
    def get_total_expenses(self):
        return self.get_expenses().aggregate(
            total = models.Sum('amount')
        )['total'] or 0

    def get_total_incomes(self):
        return self.get_incomes().aggregate(
            total = models.Sum('amount')
        )['total'] or 0
    
    def get_recent_transactions(self):
        return self.order_by('-date')[:5]
    
    def top_expense_category(self):
        return self.filter(type='expense')\
                   .values('category__name')\
                   .annotate(total=models.Sum('amount'))\
                   .order_by('-total')\
                   .first()


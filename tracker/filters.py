import django_filters
from django import forms
from tracker.models import Transaction, Category
from django.db.models import Q

class TransactionFilter(django_filters.FilterSet):
    transaction_type = django_filters.ChoiceFilter(
        choices = Transaction.TRANSACTION_TYPE_CHOICES,
        field_name = 'type', # ap dung cho truong type cua Transaction
        lookup_expr = 'iexact', # tim ban ghi chinh xac (khong phan biet hoa-thuong)
        empty_label = 'Any'  # gia tri mac dinh khi khong co lua chon trong bo loc, hien thi la Any
    )

    start_date = django_filters.DateFilter(
        field_name='date',
        lookup_expr='gte',
        label='Date From',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    end_date = django_filters.DateFilter(
        field_name='date',
        lookup_expr='lte',
        label='Date To',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    category = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.none(),
        label='Category',
        widget=forms.CheckboxSelectMultiple()
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # lấy user từ kwargs
        super().__init__(*args, **kwargs)
        if user:
            self.filters['category'].queryset = Category.objects.filter(
                Q(user=user) | Q(user__isnull=True)
        )

    class Meta:
        model = Transaction
        fields = ('transaction_type', 'start_date', 'end_date', 'category')
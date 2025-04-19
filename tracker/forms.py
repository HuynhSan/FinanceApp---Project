from django import forms
from datetime import date
from tracker.models import Transaction, Category  # Import các model cần thiết
from django.db.models import Q
from tracker.models import Category
from django.core.exceptions import ValidationError


class TransactionForm(forms.ModelForm):
    # Tùy chỉnh trường category để hiển thị dưới dạng các nút radio thay vì dropdown
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),           # Lấy tất cả các Category hiện có trong DB
        widget=forms.RadioSelect()                 # Dùng widget RadioSelect để hiển thị danh mục dạng nút tròn
    )

    date = forms.DateField(
        initial=date.today,  #Set ngày mặc định là hôm nay
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter the amount',  # Thêm placeholder cho trường số tiền
        })
    )

    type = forms.ChoiceField(
        choices=[('', 'Select transaction type')] + [
            ('income', 'Income'),  # Loại giao dịch là thu nhập
            ('expense', 'Expense'),  # Loại giao dịch là chi tiêu
        ],
        required=True
    )


    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Amount must be a positive number")
        return amount

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Lấy category mặc định + của riêng user
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=user) | Q(user__isnull=True)
            ).order_by('name')


    class Meta:
        model = Transaction                         # Gắn form này với model Transaction
        fields = (
            'type',                                 # Trường chọn loại giao dịch (thu/chi)
            'amount',                               # Trường nhập số tiền
            'date',                                 # Trường chọn ngày giao dịch
            'category',                             # Trường chọn danh mục (tùy chỉnh ở trên)
        )
        # widgets = {
        #     'date': forms.DateInput(attrs={'type': 'date'})  # Dùng input kiểu date để hiện lịch chọn ngày
        # }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Lấy user từ kwargs
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name').strip()

        # Chuẩn hóa tên để lưu: viết hoa chữ cái đầu
        normalized_name = name.capitalize()

        # Kiểm tra trùng tên với cả của user và mặc định
        qs = Category.objects.filter(name__iexact=normalized_name).filter(
            Q(user=self.user) | Q(user__isnull=True)
        )

        # Loại trừ chính instance (trong trường hợp update không đổi tên)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("This category name already exists.")

        # Kiểm tra trùng tên KHÔNG phân biệt hoa thường
        if self.user:
            if Category.objects.filter(name__iexact=normalized_name, user=self.user).exists():
                raise forms.ValidationError("This category name already exists for you.")
        else:
            if Category.objects.filter(name__iexact=normalized_name, user__isnull=True).exists():
                raise forms.ValidationError("This category name already exists as a default.")

        return normalized_name

    def save(self, commit=True):
        category = super().save(commit=False)
        if self.user:
            category.user = self.user  # Gán user tại đây
        if commit:
            category.save()
        return category

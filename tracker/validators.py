import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    def validate(self, password, user=None):
        errors = []

        # Ký tự đặc biệt
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append(_("The password must contain at least one special character (e.g., @, #, $, %, etc.)"))
        # Chữ thường
        if not re.search(r'[a-z]', password):
            errors.append(_("The password must contain at least one lowercase letter (a-z)"))

        # Số
        if not re.search(r'\d', password):
            errors.append(_("The password must contain at least one digit (0-9)"))

        # Độ dài (nếu bạn không dùng MinimumLengthValidator riêng)
        if len(password) < 8:
            errors.append(_("The password must be at least 8 characters long"))

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _(
             "Your password must be at least 8 characters long and contain at least "
            "one lowercase letter, one digit, and one special character."
        )

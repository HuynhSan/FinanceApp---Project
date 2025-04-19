from import_export import resources, fields
from tracker.models import Transaction, Category
from import_export.widgets import ForeignKeyWidget

class TransactionResource(resources.ModelResource):
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, field='name')
    )

    created_count = 0
    updated_count = 0
    skipped_count = 0

    def before_import(self, dataset, **kwargs):
        # Reset counters before import
        self.created_count = 0
        self.updated_count = 0
        self.skipped_count = 0

    def after_import_row(self, row, row_result, **kwargs):
        print("Row import type:", row_result.import_type)
        if row_result.import_type == row_result.IMPORT_TYPE_NEW:
            self.created_count += 1
        elif row_result.import_type == row_result.IMPORT_TYPE_UPDATE:
            self.updated_count += 1
        elif row_result.import_type == row_result.IMPORT_TYPE_SKIP:
            self.skipped_count += 1

    def after_init_instance(self, instance, new, row, **kwargs):
        instance.user = kwargs.get('user')

    class Meta:
        model = Transaction
        fields = ('amount', 'type', 'date', 'category')
        import_id_fields = ('amount', 'type', 'date', 'category')
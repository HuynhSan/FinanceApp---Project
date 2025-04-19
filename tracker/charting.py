import plotly.express as px
from django.db.models import Sum
from tracker.models import Category
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_income_expenses_bar_chart(qs):
    x_vals = ['Income', 'Expenditure']

    # Sum up the total income and expenditure
    total_income = qs.filter(type='income').aggregate(
        total=Sum('amount')
    )['total']
    total_expenses = qs.filter(type='expense').aggregate(
        total=Sum('amount')
    )['total']

    # Làm tròn các giá trị
    total_income = round(total_income, 2) if total_income else 0
    total_expenses = round(total_expenses, 2) if total_expenses else 0

    # Tạo biểu đồ cột
    fig = px.bar(x=x_vals, y=[total_income, total_expenses])

    # Thêm giá trị vào các cột
    fig.update_traces(text=[total_income, total_expenses], textposition='outside', texttemplate='%{text:.2f}')
    
    fig.update_layout(
        title="Total Income vs Expenditure",
        xaxis_title="Type",
        yaxis_title="Amount",
        template="plotly_dark",                # Theme tối
        plot_bgcolor="rgba(0,0,0,0)",          # Nền trong suốt
        showlegend=False,                     # Tắt legend nếu không cần
        title_x=0.5,                           # Căn giữa tiêu đề
        title_y=0.95,                          # Điều chỉnh khoảng cách tiêu đề
        title_pad={'t': 10, 'b':30}                    # Khoảng cách từ tiêu đề đến khung
    )
    return fig


def plot_category_pie_chart(qs):
    count_per_category = (
        qs.order_by('category').values('category')
        .annotate(total=Sum('amount'))
    )
    category_pks = count_per_category.values_list('category', flat=True).order_by('category')
    categories = Category.objects.filter(pk__in=category_pks).order_by('pk').values_list('name', flat=True)
    total_amounts = count_per_category.order_by('category').values_list('total', flat=True)

    # Làm tròn các giá trị
    total_amounts = [round(amount, 2) if amount else 0 for amount in total_amounts]

    # Tạo biểu đồ tròn
    fig = px.pie(values=total_amounts, names=categories)

    # Cập nhật tiêu đề và thêm giá trị lên biểu đồ
    fig.update_layout(
        title_text="Total Amount per Category",
        template="plotly_dark",  # Tùy chỉnh theme
        plot_bgcolor="rgba(0,0,0,0)",  # Làm nền trong suốt
        title_x=0.5,  # Căn giữa tiêu đề
        title_y=0.95,  # Điều chỉnh khoảng cách tiêu đề
        title_pad={'t': 10, 'b':20},  # Điều chỉnh khoảng cách từ tiêu đề đến khung
        legend=dict(x=1.05, y=0.99),  # Vị trí của legend
    )

    # Cập nhật cách hiển thị giá trị trên các lát cắt
    fig.update_traces(textinfo="percent+value", texttemplate='%{value:.2f}')

    return fig



def plot_income_expense_line_chart(qs):
    # Lấy dữ liệu tổng thu nhập và chi tiêu theo ngày
    income_data = qs.filter(type='income').values('date').annotate(total_income=Sum('amount')).order_by('date')
    expense_data = qs.filter(type='expense').values('date').annotate(total_expense=Sum('amount')).order_by('date')

    # Tạo dữ liệu cho biểu đồ đường
    income_dates = [entry['date'] for entry in income_data]
    income_amounts = [round(entry['total_income'], 2) for entry in income_data]  # Làm tròn đến 2 chữ số thập phân

    expense_dates = [entry['date'] for entry in expense_data]
    expense_amounts = [round(entry['total_expense'], 2) for entry in expense_data]  # Làm tròn đến 2 chữ số thập phân

    # Vẽ biểu đồ đường
    fig = go.Figure()

    # Thêm đường cho thu nhập
    fig.add_trace(go.Scatter(
        x=income_dates,
        y=income_amounts,
        mode='lines+markers+text',  # Đường, điểm dữ liệu và giá trị hiển thị
        name='Income',
        line=dict(color='green', width=3),  # Màu sắc và độ dày đường
        marker=dict(size=8, color='green', symbol='circle'),  # Điểm dữ liệu
        text=income_amounts,  # Hiển thị giá trị trên điểm
        textposition='top center',  # Vị trí hiển thị giá trị
        textfont=dict(size=10, color='green'),  # Tùy chỉnh font của giá trị
    ))

    # Thêm đường cho chi tiêu
    fig.add_trace(go.Scatter(
        x=expense_dates,
        y=expense_amounts,
        mode='lines+markers+text',  # Đường, điểm dữ liệu và giá trị hiển thị
        name='Expense',
        line=dict(color='red', width=3),  # Màu sắc và độ dày đường
        marker=dict(size=8, color='red', symbol='circle'),  # Điểm dữ liệu
        text=expense_amounts,  # Hiển thị giá trị trên điểm
        textposition='top center',  # Vị trí hiển thị giá trị
        textfont=dict(size=10, color='red'),  # Tùy chỉnh font của giá trị
    ))

    # Tùy chỉnh layout
    fig.update_layout(
        title="Income vs Expense Over Time",
        xaxis_title="Date",
        yaxis_title="Amount",
        template="plotly_dark",  # Thêm theme đẹp
        xaxis=dict(tickformat="%b %d, %Y"),  # Định dạng ngày tháng
        legend=dict(x=0.01, y=0.99),  # Vị trí của legend
        plot_bgcolor="rgba(0,0,0,0)",  # Màu nền trong suốt
        title_x=0.5,  # Căn giữa tiêu đề
        title_y=0.95,  # Điều chỉnh khoảng cách tiêu đề
        title_pad={'t': 10}  # Điều chỉnh khoảng cách từ tiêu đề đến khung
    )

    return fig



def plot_monthly_comparison_line_chart(current_month_data, previous_month_data, selected_month, selected_previous_month):
    """
    Vẽ biểu đồ đường so sánh thu nhập và chi tiêu giữa tháng hiện tại và tháng trước.

    :param current_month_data: Dữ liệu giao dịch tháng hiện tại (QuerySet)
    :param previous_month_data: Dữ liệu giao dịch tháng trước (QuerySet)
    :param selected_month: Tháng hiện tại (int)
    :param selected_previous_month: Tháng trước (int)
    :return: Biểu đồ Plotly
    """
    # Tính tổng thu nhập và chi tiêu của tháng hiện tại
    current_month_income = current_month_data.get_total_incomes()
    current_month_expense = current_month_data.get_total_expenses()

    # Tính tổng thu nhập và chi tiêu của tháng trước
    previous_month_income = previous_month_data.get_total_incomes()
    previous_month_expense = previous_month_data.get_total_expenses()

    # Dữ liệu cho biểu đồ
    months = [f"Month {selected_previous_month}", f"Month {selected_month}"]  # Tên các tháng
    income_values = [previous_month_income, current_month_income]  # Thu nhập
    expense_values = [previous_month_expense, current_month_expense]  # Chi tiêu

    # Tạo subplots
    fig = make_subplots(
        rows=1, cols=1,
        shared_xaxes=True
    )

    # Thêm đường biểu diễn thu nhập (Income)
    fig.add_trace(
        go.Scatter(
            x=months,
            y=income_values,
            mode='lines+markers+text',  # Hiển thị các chỉ số (text)
            name='Income',
            line=dict(color='green', width=3, dash='solid'),  # Đường thu nhập màu xanh lá
            marker=dict(symbol='circle', size=8, color='green'),
            text=[f"{value:,.0f}₫" for value in income_values],  # Chỉ số thu nhập
            textposition="top center",  # Vị trí của chỉ số trên biểu đồ
        ),
        row=1, col=1
    )

    # Thêm đường biểu diễn chi tiêu (Expense)
    fig.add_trace(
        go.Scatter(
            x=months,
            y=expense_values,
            mode='lines+markers+text',  # Hiển thị các chỉ số (text)
            name='Expense',
            line=dict(color='red', width=3, dash='dot'),  # Đường chi tiêu màu đỏ
            marker=dict(symbol='square', size=8, color='red'),
            text=[f"{value:,.0f}₫" for value in expense_values],  # Chỉ số chi tiêu
            textposition="top center",  # Vị trí của chỉ số trên biểu đồ
        ),
        row=1, col=1
    )

    # Cập nhật layout của biểu đồ
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Amount",
        template="plotly_white",  # Thêm theme tùy chọn
        showlegend=True,  # Hiển thị legend
        legend=dict(
            x=1,  # Đặt legend ở vị trí bên phải
            y=1.3,  # Đặt legend ở vị trí trên cùng
            xanchor='left',  # Điều chỉnh điểm neo của legend
            yanchor='top',  # Điều chỉnh điểm neo của legend
            orientation='v',  # Đặt legend theo chiều dọc
            title="Type",  # Tiêu đề của legend
        ),
        plot_bgcolor="rgba(0,0,0,0)",  # Làm nền trong suốt
        height=450  # Chiều cao biểu đồ
    )

    return fig


from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from accounts.views import home, author_dashboard, author_signup
from sales.views import receiving_view, sales_view
from payouts.views import payout_view
from catalog.views import create_book
from catalog.views import create_book, book_options
from sales.views import receiving_view, sales_view, receiving_tables_partial, sales_tables_partial

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("accounts/signup/", author_signup, name="author_signup"),
    path("", home, name="home"),
    path("author/dashboard/", author_dashboard, name="author_dashboard"),
    path("author/books/new/", create_book, name="author_book_new"),
    path("staff/receiving/", receiving_view, name="receiving"),
    path("staff/sales/", sales_view, name="sales"),
    path("staff/payouts/", payout_view, name="payouts"),
    path("ajax/book-options/", book_options, name="book_options"),
    path("ajax/receiving-tables/", receiving_tables_partial, name="receiving_tables_partial"),
    path("ajax/sales-tables/", sales_tables_partial, name="sales_tables_partial"),
]

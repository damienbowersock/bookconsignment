# sales/views.py
from urllib.parse import parse_qs
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum, F
from accounts.views import in_group
from accounts.models import AuthorProfile
from catalog.models import Book
from consignment.models import ConsignmentItem, ConsignmentBatch
from .forms import ConsignmentReceiptForm, SaleForm
from .models import Sale
from django.template.loader import render_to_string
from django.http import HttpResponse


def _get_selected_author(request):
    """Parse ?author=<id> from the raw query string (robust even if request.GET is shadowed)."""
    qs = parse_qs(request.META.get("QUERY_STRING", ""))
    author_vals = qs.get("author", [])
    if not author_vals:
        return None
    try:
        return AuthorProfile.objects.select_related("user").get(pk=int(author_vals[0]))
    except (ValueError, AuthorProfile.DoesNotExist):
        return None


@login_required
@user_passes_test(lambda u: in_group(u, "Staff"))
def receiving_tables_partial(request):
    """Return only the Receiving tables HTML (recent consignment items), filtered by ?author=."""
    selected_author = _get_selected_author(request)

    items = (
        ConsignmentItem.objects
        .select_related("book", "batch__location", "book__author__user")
        .order_by("-created_at")
    )
    if selected_author:
        items = items.filter(book__author=selected_author)
    items = items[:20]

    html = render_to_string(
        "staff/partials/receiving_tables.html",
        {"receipts": items, "selected_author": selected_author},
        request=request,
    )
    return HttpResponse(html)


@login_required
@user_passes_test(lambda u: in_group(u, "Staff"))
def sales_tables_partial(request):
    """Return only the Sales tables HTML (recent sales + stock), filtered by ?author=."""
    selected_author = _get_selected_author(request)

    recent = (
        Sale.objects
        .select_related("book", "location", "book__author__user")
        .order_by("-sold_at")
    )
    if selected_author:
        recent = recent.filter(book__author=selected_author)
    recent = recent[:20]

    # Stock snapshot (consigned - sold), optionally filtered
    stock = (
        ConsignmentItem.objects.values("book__title", "book__author")
        .annotate(qty_in=Sum("quantity_consigned"))
    )
    if selected_author:
        stock = stock.filter(book__author=selected_author)

    sales = (
        Sale.objects.values("book__title", "book__author")
        .annotate(qty_out=Sum("quantity"), revenue=Sum(F("quantity") * F("unit_price")))
    )
    if selected_author:
        sales = sales.filter(book__author=selected_author)

    out_map = {s["book__title"]: s["qty_out"] or 0 for s in sales}
    rows = []
    for r in stock:
        title = r["book__title"]
        rows.append({
            "title": title,
            "on_hand": (r["qty_in"] or 0) - (out_map.get(title, 0) or 0),
        })

    html = render_to_string(
        "staff/partials/sales_tables.html",
        {"recent": recent, "stock": rows, "selected_author": selected_author},
        request=request,
    )
    return HttpResponse(html)


@login_required
@user_passes_test(lambda u: in_group(u, "Staff"))
def receiving_view(request):
    selected_author = _get_selected_author(request)
    books_qs = Book.objects.all()
    if selected_author:
        books_qs = books_qs.filter(author=selected_author)

    if request.method == "POST":
        form = ConsignmentReceiptForm(request.POST)
        form.fields["book"].queryset = books_qs
        if form.is_valid():
            # Create consignment batch and item
            book = form.cleaned_data["book"]
            location = form.cleaned_data["location"]
            qty = form.cleaned_data["qty"]

            # Get or create a batch for today
            from django.utils import timezone
            batch, _ = ConsignmentBatch.objects.get_or_create(
                author=book.author,
                org=location.org,
                location=location,
                received_date=timezone.now().date(),
                status="active",
                defaults={
                    "created_by": request.user,
                }
            )

            ConsignmentItem.objects.create(
                batch=batch,
                book=book,
                quantity_consigned=qty,
                created_by=request.user,
            )

            messages.success(request, "Inventory received.")
            suffix = f"?author={selected_author.id}" if selected_author else ""
            return redirect(f"{reverse('receiving')}{suffix}")
    else:
        form = ConsignmentReceiptForm()
        form.fields["book"].queryset = books_qs

    items = (
        ConsignmentItem.objects
        .select_related("book", "batch__location", "book__author__user")
        .order_by("-created_at")
    )
    if selected_author:
        items = items.filter(book__author=selected_author)
    items = items[:20]

    authors = AuthorProfile.objects.select_related("user").order_by(
        "user__last_name", "user__first_name"
    )

    return render(request, "staff/receiving.html", {
        "form": form,
        "receipts": items,
        "authors": authors,
        "selected_author": selected_author,
    })


@login_required
@user_passes_test(lambda u: in_group(u, "Staff"))
def sales_view(request):
    selected_author = _get_selected_author(request)
    books_qs = Book.objects.all()
    if selected_author:
        books_qs = books_qs.filter(author=selected_author)

    if request.method == "POST":
        form = SaleForm(request.POST)
        form.fields["book"].queryset = books_qs
        if form.is_valid():
            sale = form.save(commit=False)
            # Set org from location
            sale.org = sale.location.org
            # Set author share rate (use default for now)
            sale.author_share_rate = sale.org.default_author_share
            sale.created_by = request.user
            sale.save()
            messages.success(request, "Sale recorded.")
            suffix = f"?author={selected_author.id}" if selected_author else ""
            return redirect(f"{reverse('sales')}{suffix}")
    else:
        form = SaleForm()
        form.fields["book"].queryset = books_qs

    recent = (
        Sale.objects
        .select_related("book", "location", "book__author__user")
        .order_by("-sold_at")
    )
    if selected_author:
        recent = recent.filter(book__author=selected_author)
    recent = recent[:20]

    stock = (
        ConsignmentItem.objects.values("book__title", "book__author")
        .annotate(qty_in=Sum("quantity_consigned"))
    )
    if selected_author:
        stock = stock.filter(book__author=selected_author)

    sales = (
        Sale.objects.values("book__title", "book__author")
        .annotate(qty_out=Sum("quantity"), revenue=Sum(F("quantity") * F("unit_price")))
    )
    if selected_author:
        sales = sales.filter(book__author=selected_author)

    out_map = {s["book__title"]: s["qty_out"] or 0 for s in sales}
    rows = []
    for r in stock:
        title = r["book__title"]
        rows.append({
            "title": title,
            "on_hand": (r["qty_in"] or 0) - (out_map.get(title, 0) or 0),
        })

    authors = AuthorProfile.objects.select_related("user").order_by(
        "user__last_name", "user__first_name"
    )

    return render(request, "staff/sales.html", {
        "form": form,
        "recent": recent,
        "stock": rows,
        "authors": authors,
        "selected_author": selected_author,
    })

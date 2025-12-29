from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.db.models import Sum, F
from django.shortcuts import render, redirect
from .models import AuthorProfile, AuthorOrganization
from catalog.models import Book
from payouts.models import Payout
from sales.models import Sale
from consignment.models import ConsignmentItem
from .forms import AuthorSignupForm


def in_group(user, group_name: str) -> bool:
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


def home(request):
    if not request.user.is_authenticated:
        return render(request, "home.html", {"role": "guest"})
    if in_group(request.user, "Staff"):
        return render(request, "home.html", {"role": "staff"})
    elif in_group(request.user, "Authors"):
        return redirect("author_dashboard")
    else:
        return render(request, "home.html", {"role": "unknown"})


def author_signup(request):
    if request.user.is_authenticated:
        if in_group(request.user, "Authors"):
            return redirect("author_dashboard")
        if in_group(request.user, "Staff"):
            return redirect("home")
    if request.method == "POST":
        form = AuthorSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.save()

            org = form.cleaned_data["org"]
            phone = form.cleaned_data.get("phone", "")
            author_profile = AuthorProfile.objects.create(user=user, phone=phone)

            # Create author-organization relationship
            AuthorOrganization.objects.create(
                author=author_profile,
                org=org,
                status="active",
            )

            authors_group, _ = Group.objects.get_or_create(name="Authors")
            user.groups.add(authors_group)

            login(request, user)
            return redirect("author_dashboard")
    else:
        form = AuthorSignupForm()
    return render(request, "author/signup.html", {"form": form})


def author_dashboard(request):
    if not request.user.is_authenticated or not in_group(request.user, "Authors"):
        return redirect("login")
    try:
        author = request.user.author_profile
    except Exception:
        return render(request, "author/dashboard.html", {"error": "No Author profile assigned."})

    books = Book.objects.filter(author=author)

    # Get consignment data from ConsignmentItem
    inv = (
        ConsignmentItem.objects.filter(book__in=books)
        .values("book__id", "book__title")
        .annotate(qty_in=Sum("quantity_consigned"))
    )

    # Get sales data
    sales = (
        Sale.objects.filter(book__in=books)
        .values("book__id", "book__title")
        .annotate(
            qty_out=Sum("quantity"),
            revenue=Sum(F("quantity") * F("unit_price")),
            author_earnings_total=Sum("author_earnings"),
        )
    )

    qty_out_map = {s["book__id"]: s.get("qty_out") or 0 for s in sales}
    revenue_map = {s["book__id"]: s.get("revenue") or 0 for s in sales}
    earnings_map = {s["book__id"]: s.get("author_earnings_total") or 0 for s in sales}

    rows = []
    total_author_due = 0
    for rec in inv:
        book_id = rec["book__id"]
        title = rec["book__title"]
        qty_in = rec.get("qty_in") or 0
        qty_out = qty_out_map.get(book_id, 0) or 0
        on_hand = qty_in - qty_out
        revenue = revenue_map.get(book_id, 0) or 0
        author_due = float(earnings_map.get(book_id, 0) or 0)
        total_author_due += author_due
        rows.append({
            "title": title,
            "on_hand": on_hand,
            "sold": qty_out,
            "revenue": revenue,
            "author_due": author_due,
        })

    paid = Payout.objects.filter(author=author, status="completed").aggregate(
        total=Sum("amount")
    )["total"] or 0
    balance = total_author_due - float(paid)

    payouts = Payout.objects.filter(author=author).order_by("-created_at")

    context = {
        "rows": rows,
        "total_revenue": sum(r["revenue"] for r in rows),
        "total_author_due": total_author_due,
        "total_paid": paid,
        "balance": balance,
        "payouts": payouts,
    }
    return render(request, "author/dashboard.html", context)

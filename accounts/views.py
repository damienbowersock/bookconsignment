from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.db.models import Sum, F
from django.shortcuts import render, redirect
from .models import AuthorProfile
from catalog.models import Book
from payouts.models import Payout
from sales.models import InventoryReceipt, Sale
from consignment.models import ConsignmentAgreement
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
            AuthorProfile.objects.create(user=user, org=org, phone=phone)

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
        author = request.user.authorprofile
    except Exception:
        return render(request, "author/dashboard.html", {"error": "No Author profile assigned."})

    books = Book.objects.filter(author=author)

    inv = (
        InventoryReceipt.objects.filter(book__in=books)
        .values("book__id", "book__title")
        .annotate(qty_in=Sum("qty"))
    )

    sales = (
        Sale.objects.filter(book__in=books)
        .values("book__id", "book__title")
        .annotate(qty_out=Sum("qty"), revenue=Sum(F("qty") * F("unit_price")))
    )

    qty_out_map = {s["book__id"]: s.get("qty_out") or 0 for s in sales}
    revenue_map = {s["book__id"]: s.get("revenue") or 0 for s in sales}

    shares = {}
    for b in books:
        ag = ConsignmentAgreement.objects.filter(book=b, author=author).order_by("-start").first()
        shares[b.id] = ag.author_share if ag else 0.6

    rows = []
    total_author_due = 0
    for rec in inv:
        book_id = rec["book__id"]
        title = rec["book__title"]
        qty_in = rec.get("qty_in") or 0
        qty_out = qty_out_map.get(book_id, 0) or 0
        on_hand = qty_in - qty_out
        revenue = revenue_map.get(book_id, 0) or 0
        share = shares.get(book_id, 0.6)
        author_due = float(revenue) * float(share)
        total_author_due += author_due
        rows.append({
            "title": title, "on_hand": on_hand, "sold": qty_out,
            "revenue": revenue, "author_share": share, "author_due": author_due
        })

    paid = Payout.objects.filter(author=author).aggregate(total=Sum("amount"))["total"] or 0
    balance = total_author_due - float(paid)

    payouts = Payout.objects.filter(author=author).order_by("-paid_at")

    context = {
        "rows": rows,
        "total_revenue": sum(r["revenue"] for r in rows),
        "total_author_due": total_author_due,
        "total_paid": paid,
        "balance": balance,
        "payouts": payouts,
    }
    return render(request, "author/dashboard.html", context)

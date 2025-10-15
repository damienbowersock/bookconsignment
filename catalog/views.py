from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from accounts.views import in_group
from accounts.models import AuthorProfile
from .forms import BookForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from catalog.models import Book

def book_options(request):
    """Return <option> tags for the Book <select>, optionally filtered by ?author=<id>."""
    author_id = request.GET.get("author")
    books = Book.objects.all().select_related("author")
    if author_id:
        try:
            books = books.filter(author_id=int(author_id))
        except ValueError:
            books = books.none()
    html = render_to_string("partials/book_options.html", {"books": books})
    return HttpResponse(html)

@login_required
def create_book(request):
    if not in_group(request.user, "Authors"):
        messages.error(request, "Only authors can add books.")
        return redirect("home")
    try:
        author_profile = request.user.authorprofile
    except AuthorProfile.DoesNotExist:
        messages.error(request, "No Author profile assigned to your account.")
        return redirect("author_dashboard")

    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.author = author_profile
            book.save()
            messages.success(request, "Book added to your catalog.")
            return redirect("author_dashboard")
    else:
        form = BookForm()
    return render(request, "author/book_form.html", {"form": form})

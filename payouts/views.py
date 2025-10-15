from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.views import in_group
from .forms import PayoutForm
from .models import Payout

@login_required
@user_passes_test(lambda u: in_group(u, "Staff"))
def payout_view(request):
    if request.method == "POST":
        form = PayoutForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Payout recorded.")
            return redirect("payouts")
    else:
        form = PayoutForm()
    recent = Payout.objects.select_related("author").order_by("-paid_at")[:20]
    return render(request, "staff/payout.html", {"form": form, "recent": recent})

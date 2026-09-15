from collections import defaultdict
from decimal import Decimal, InvalidOperation

from django.http import HttpResponseNotAllowed
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import Expense, Invitation, Member, Trip

categories = ["Food & drinks", "Stay", "Transport", "Activities", "Other"]
COLORS = ["#f4a261", "#5b8e7d", "#e76f51", "#8d6e9f", "#3a86ff", "#e9c46a"]

def current_trip(request):
    trip_id = request.GET.get("trip") or request.POST.get("trip") or request.COOKIES.get("splitwisely_trip")
    visible_trips = Trip.objects.filter(owner=request.user) | Trip.objects.filter(members__user=request.user) | Trip.objects.filter(invitations__recipient=request.user, invitations__status="pending")
    trip = visible_trips.filter(id=trip_id).first() if trip_id else visible_trips.first()
    if trip is None:
        trip = Trip.objects.create(name="Goa getaway", location="Goa", date_label="12–16 Feb")
        for index, name in enumerate(["Aarav", "Meera", "Kabir", "Priya", "Rohan", "Nisha"]):
            Member.objects.create(trip=trip, name=name, color=COLORS[index])
        seed = [
            ("Villa stay", "Stay", 840, "Meera", ["Aarav", "Meera", "Kabir", "Priya", "Rohan", "Nisha"], "Day 1", "4 nights near Candolim"),
            ("Airport cabs", "Transport", 68, "Aarav", ["Aarav", "Meera", "Kabir", "Priya", "Rohan", "Nisha"], "Day 1", "Both ways"),
            ("Dinner at Gunpowder", "Food & drinks", 212, "Kabir", ["Aarav", "Meera", "Kabir", "Rohan", "Nisha"], "Day 2", "Priya skipped beer"),
            ("Scuba diving", "Activities", 320, "Rohan", ["Aarav", "Meera", "Kabir", "Rohan"], "Day 3", "4 divers"),
            ("2am chai & snacks", "Food & drinks", 24, "Nisha", ["Aarav", "Nisha", "Priya"], "Day 3", "The important one"),
        ]
        for title, category, amount, payer, participant_names, day, note in seed:
            expense = Expense.objects.create(trip=trip, title=title, category=category, amount=amount, paid_by=trip.members.get(name=payer), day=day, note=note)
            expense.participants.set(trip.members.filter(name__in=participant_names))
    if trip.owner_id is None:
        trip.owner = request.user
        trip.save(update_fields=["owner"])
    return trip

def accessible_trip(request, trip_id):
    return get_object_or_404(Trip.objects.filter(owner=request.user) | Trip.objects.filter(members__user=request.user), id=trip_id)

def settle(balances):
    creditors = [[item["name"], item["net"]] for item in balances if item["net"] > 0.005]
    debtors = [[item["name"], -item["net"]] for item in balances if item["net"] < -0.005]
    creditors.sort(key=lambda item: item[1], reverse=True); debtors.sort(key=lambda item: item[1], reverse=True)
    result = []; ci = di = 0
    while ci < len(creditors) and di < len(debtors):
        amount = round(min(creditors[ci][1], debtors[di][1]), 2)
        result.append({"from": debtors[di][0], "to": creditors[ci][0], "amount": amount})
        debtors[di][1] -= amount; creditors[ci][1] -= amount
        if debtors[di][1] < .01: di += 1
        if creditors[ci][1] < .01: ci += 1
    return result

def context_data(trip, user):
    members = list(trip.members.all()); expenses = list(trip.expenses.select_related("paid_by").prefetch_related("participants"))
    paid = defaultdict(float); owed = defaultdict(float)
    for expense in expenses:
        paid[expense.paid_by.name] += float(expense.amount)
        participants = list(expense.participants.all())
        for member in participants: owed[member.name] += float(expense.amount) / len(participants)
    balances = [{"name": member.name, "paid": round(paid[member.name], 2), "owed": round(owed[member.name], 2), "net": round(paid[member.name] - owed[member.name], 2), "absolute_net": abs(round(paid[member.name] - owed[member.name], 2))} for member in members]
    total = sum(float(item.amount) for item in expenses)
    visible_trips = Trip.objects.filter(owner=user) | Trip.objects.filter(members__user=user)
    return {"trip": trip, "trips": visible_trips.distinct(), "members": members, "expenses": expenses, "total": total, "each_person": total / len(members) if members else 0, "balances": balances, "top_spender": max(balances, key=lambda item: item["paid"], default={"name": "Nobody", "paid": 0}), "settlements": settle(balances), "categories": categories, "invitations": Invitation.objects.filter(recipient=user, status="pending").select_related("trip", "inviter")}

@login_required
def dashboard(request):
    trip = current_trip(request); context = context_data(trip, request.user); query = request.GET.get("q", "").lower(); category = request.GET.get("category", "All expenses")
    context.update({"query": request.GET.get("q", ""), "category": category, "filtered_expenses": [item for item in context["expenses"] if (not query or query in f"{item.title} {item.category} {item.paid_by.name} {item.note}".lower()) and (category == "All expenses" or item.category == category)]})
    response = render(request, "trip/dashboard.html", context)
    response.set_cookie("splitwisely_trip", str(trip.id), max_age=60 * 60 * 24 * 365)
    return response

@login_required
def settle_up(request):
    return render(request, "trip/settle_up.html", context_data(current_trip(request), request.user))

def form_context(trip, expense=None, user=None):
    visible_trips = Trip.objects.filter(owner=user) | Trip.objects.filter(members__user=user)
    return {"trip": trip, "trips": visible_trips.distinct(), "members": trip.members.all(), "categories": categories, "expense": expense}

def parse_payload(request):
    try: amount = Decimal(request.POST.get("amount", "0"))
    except InvalidOperation: amount = Decimal("0")
    return {"title": request.POST.get("title", "").strip(), "category": request.POST.get("category", "Other"), "amount": amount, "paid_by": request.POST.get("paid_by", ""), "participant_ids": request.POST.getlist("participants"), "day": request.POST.get("day", "Day 1"), "note": request.POST.get("note", "").strip()}

def save_expense(request, trip, expense=None):
    payload = parse_payload(request); member_map = {str(member.id): member for member in trip.members.all()}; participants = [member_map[item] for item in payload.pop("participant_ids") if item in member_map]
    payer = member_map.get(payload.pop("paid_by"))
    if not payload["title"] or payload["amount"] <= 0 or not payer or not participants: return render(request, "trip/expense_form.html", {**form_context(trip, expense, request.user), "error": "Add a name, amount, payer, and at least one participant."}, status=422)
    if expense is None: expense = Expense(trip=trip)
    for key, value in payload.items(): setattr(expense, key, value)
    expense.paid_by = payer; expense.save(); expense.participants.set(participants); return redirect(f"/?trip={trip.id}")

@require_http_methods(["GET", "POST"])
@login_required
def add_expense(request):
    trip = current_trip(request)
    return render(request, "trip/expense_form.html", form_context(trip, user=request.user)) if request.method == "GET" else save_expense(request, trip)

@require_http_methods(["GET", "POST"])
@login_required
def edit_expense(request, expense_id):
    trip = current_trip(request); expense = get_object_or_404(Expense, id=expense_id, trip=trip)
    return render(request, "trip/expense_form.html", form_context(trip, expense, request.user)) if request.method == "GET" else save_expense(request, trip, expense)

@login_required
def delete_expense(request, expense_id):
    if request.method != "POST": return HttpResponseNotAllowed(["POST"])
    expense = get_object_or_404(Expense, id=expense_id, trip=current_trip(request)); expense.delete(); return redirect(f"/?trip={expense.trip_id}")

@require_http_methods(["GET", "POST"])
@login_required
def new_trip(request):
    if request.method == "GET": return render(request, "trip/new_trip.html", {"trip": Trip.objects.first(), "trips": Trip.objects.filter(owner=request.user)})
    name = request.POST.get("name", "").strip(); location = request.POST.get("location", "").strip() or "A new adventure"
    if not name: return render(request, "trip/new_trip.html", {"trip": Trip.objects.first(), "trips": Trip.objects.filter(owner=request.user), "error": "Give this trip a name."}, status=422)
    trip = Trip.objects.create(name=name, location=location, date_label=request.POST.get("date_label", ""), owner=request.user)
    Member.objects.create(trip=trip, user=request.user, name=request.user.get_full_name() or request.user.username, email=request.user.email, color=COLORS[0])
    return redirect(f"/expenses/add/?trip={trip.id}")

@require_http_methods(["GET", "POST"])
@login_required
def add_member(request, trip_id):
    trip = accessible_trip(request, trip_id)
    if request.method == "GET": return render(request, "trip/add_member.html", {"trip": trip, "trips": Trip.objects.filter(owner=request.user) | Trip.objects.filter(members__user=request.user)})
    email = request.POST.get("email", "").strip().lower()
    if email:
        recipient = User.objects.filter(email__iexact=email).first()
        Invitation.objects.update_or_create(trip=trip, email=email, defaults={"inviter": request.user, "recipient": recipient, "status": "pending"})
    return redirect(f"/?trip={trip.id}")

@login_required
@require_http_methods(["POST"])
def respond_invitation(request, invitation_id, response):
    invitation = get_object_or_404(Invitation, id=invitation_id, recipient=request.user, status="pending")
    invitation.status = "accepted" if response == "accept" else "declined"
    invitation.save(update_fields=["status"])
    if invitation.status == "accepted":
        Member.objects.get_or_create(trip=invitation.trip, user=request.user, defaults={"name": request.user.get_full_name() or request.user.username, "email": request.user.email, "color": COLORS[invitation.trip.members.count() % len(COLORS)]})
    return redirect("dashboard")

@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == "GET": return render(request, "trip/signup.html")
    email = request.POST.get("email", "").strip().lower(); password = request.POST.get("password", "")
    if not email or not password: return render(request, "trip/signup.html", {"error": "Email and password are required."}, status=422)
    if User.objects.filter(email__iexact=email).exists(): return render(request, "trip/signup.html", {"error": "That email is already registered."}, status=422)
    user = User.objects.create_user(username=email, email=email, password=password)
    Invitation.objects.filter(email=email, status="pending").update(recipient=user)
    login(request, user); return redirect("new_trip")

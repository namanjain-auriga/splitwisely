from decimal import Decimal

from django.contrib.auth import authenticate, get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Expense, Invitation, Member, Trip
from .views import context_data, settle

User = get_user_model()


class AccountAndTripTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner@example.com",
            email="owner@example.com",
            password="strong-password-123",
        )
        self.guest = User.objects.create_user(
            username="guest@example.com",
            email="guest@example.com",
            password="strong-password-123",
        )

    def test_login_accepts_email_and_username(self):
        self.assertEqual(authenticate(username="owner@example.com", password="strong-password-123"), self.owner)
        self.assertEqual(authenticate(username="owner", password="strong-password-123"), None)
        self.owner.username = "owner"
        self.owner.save(update_fields=["username"])
        self.assertEqual(authenticate(username="owner", password="strong-password-123"), self.owner)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, "/login/?next=/")

    def test_signup_uses_email_as_account_identity(self):
        response = self.client.post(reverse("signup"), {"email": "new@example.com", "password": "strong-password-123"})
        self.assertRedirects(response, reverse("new_trip"))
        new_user = User.objects.get(email="new@example.com")
        self.assertEqual(new_user.username, "new@example.com")
        self.assertEqual(int(self.client.session["_auth_user_id"]), new_user.id)

    def test_new_trip_makes_creator_owner_and_first_member(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("new_trip"), {"name": "Beach weekend", "location": "Goa", "date_label": "12–16 Feb"})
        trip = Trip.objects.get(name="Beach weekend")
        self.assertRedirects(response, f"/expenses/add/?trip={trip.id}")
        member = trip.members.get(user=self.owner)
        self.assertEqual(trip.owner, self.owner)
        self.assertEqual(member.email, self.owner.email)


class InvitationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner@example.com", email="owner@example.com", password="pass-12345")
        self.guest = User.objects.create_user(username="guest@example.com", email="guest@example.com", password="pass-12345")
        self.trip = Trip.objects.create(owner=self.owner, name="Shared Goa", location="Goa")
        Member.objects.create(trip=self.trip, user=self.owner, name="Owner", email=self.owner.email)
        self.client.force_login(self.owner)

    def test_invitation_is_pending_until_recipient_accepts(self):
        self.client.post(reverse("add_member", args=[self.trip.id]), {"email": self.guest.email})
        invitation = Invitation.objects.get(trip=self.trip, email=self.guest.email)
        self.assertEqual(invitation.status, "pending")
        self.assertFalse(Member.objects.filter(trip=self.trip, user=self.guest).exists())

        self.client.force_login(self.guest)
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, self.owner.email)
        self.assertContains(response, self.trip.name)
        self.client.post(reverse("respond_invitation", args=[invitation.id, "accept"]))
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, "accepted")
        self.assertTrue(Member.objects.filter(trip=self.trip, user=self.guest).exists())

    def test_declining_invitation_does_not_create_membership(self):
        self.client.post(reverse("add_member", args=[self.trip.id]), {"email": self.guest.email})
        invitation = Invitation.objects.get(trip=self.trip)
        self.client.force_login(self.guest)
        self.client.post(reverse("respond_invitation", args=[invitation.id, "decline"]))
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, "declined")
        self.assertFalse(Member.objects.filter(trip=self.trip, user=self.guest).exists())

    def test_user_cannot_view_another_users_trip(self):
        self.client.force_login(self.guest)
        response = self.client.get(reverse("dashboard"), {"trip": self.trip.id})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.trip.name)


class ExpenseAndSettlementTests(TestCase):
    def test_participant_specific_expense_is_used_for_balances(self):
        owner = User.objects.create_user(username="owner@example.com", email="owner@example.com", password="pass-12345")
        trip = Trip.objects.create(owner=owner, name="Scuba trip")
        payer = Member.objects.create(trip=trip, user=owner, name="Payer", email=owner.email)
        diver = Member.objects.create(trip=trip, name="Diver")
        excluded = Member.objects.create(trip=trip, name="Excluded")
        expense = Expense.objects.create(trip=trip, title="Scuba", category="Activities", amount=Decimal("300.00"), paid_by=payer)
        expense.participants.set([payer, diver])
        balances = context_data(trip, owner)["balances"]
        self.assertEqual(next(item for item in balances if item["name"] == "Payer")["owed"], 150.0)
        self.assertEqual(next(item for item in balances if item["name"] == "Excluded")["owed"], 0.0)

    def test_settlement_matches_creditors_and_debtors(self):
        balances = [
            {"name": "A", "net": -60},
            {"name": "B", "net": -40},
            {"name": "C", "net": 100},
        ]
        self.assertEqual(settle(balances), [
            {"from": "A", "to": "C", "amount": 60},
            {"from": "B", "to": "C", "amount": 40},
        ])

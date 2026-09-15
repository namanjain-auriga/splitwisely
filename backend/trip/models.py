from django.db import models
from django.contrib.auth.models import User

class Trip(models.Model):
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="owned_trips")
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=120, default="Goa")
    date_label = models.CharField(max_length=80, default="12–16 Feb")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

class Member(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="trip_memberships")
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="members")
    name = models.CharField(max_length=80)
    email = models.EmailField(blank=True)
    color = models.CharField(max_length=7, default="#5b8e7d")

    class Meta:
        unique_together = ["trip", "name"]
        ordering = ["id"]

    @property
    def initials(self):
        return "".join(part[0] for part in self.name.split()[:2]).upper()

class Invitation(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("accepted", "Accepted"), ("declined", "Declined")]
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="invitations")
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_invitations")
    recipient = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="received_invitations")
    email = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["trip", "email"], name="one_trip_invitation_per_email")]

class Expense(models.Model):
    CATEGORY_CHOICES = [(item, item) for item in ["Stay", "Food & drinks", "Transport", "Activities", "Other"]]
    DAY_CHOICES = [(f"Day {number}", f"Day {number}") for number in range(1, 5)]
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="expenses")
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_by = models.ForeignKey(Member, on_delete=models.PROTECT, related_name="paid_expenses")
    participants = models.ManyToManyField(Member, related_name="shared_expenses")
    day = models.CharField(max_length=10, choices=DAY_CHOICES, default="Day 1")
    note = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="trip/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),
    path("", views.dashboard, name="dashboard"),
    path("settle-up/", views.settle_up, name="settle_up"),
    path("expenses/add/", views.add_expense, name="add_expense"),
    path("expenses/<int:expense_id>/edit/", views.edit_expense, name="edit_expense"),
    path("expenses/<int:expense_id>/delete/", views.delete_expense, name="delete_expense"),
    path("trips/new/", views.new_trip, name="new_trip"),
    path("trips/<int:trip_id>/members/add/", views.add_member, name="add_member"),
    path("invitations/<int:invitation_id>/<str:response>/", views.respond_invitation, name="respond_invitation"),
]
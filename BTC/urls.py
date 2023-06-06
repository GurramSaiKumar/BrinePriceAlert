from django.urls import path
from BTC.views import test
from BTC.views import CreateAlertView, LoginView, DeleteAlertView, AlertsListView

urlpatterns = [
    path('', test, name="test"),
    # to get JWT token
    path('login/', LoginView.as_view(), name='login'),
    # to create an alert
    path('alerts/create/', CreateAlertView.as_view(), name='create_alert'),
    # to delete an alert
    path('alerts/delete/', DeleteAlertView.as_view(), name='delete_alert'),
    # to list all alerts
    path('alerts/list/', AlertsListView.as_view(), name='alerts-list'),

]

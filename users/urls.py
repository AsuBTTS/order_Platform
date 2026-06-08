from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("stores/", views.store_list_view, name="stores"),
    path("user/current/", views.current_user_view, name="current-user"),
    path("user/profile/", views.update_profile_view, name="update-profile"),
    path("user/change-password/", views.change_password_view, name="change-password"),
    path("user/coupons/", views.user_coupons_view, name="user-coupons"),
    path("platform/dashboard/", views.platform_dashboard_view, name="platform-dashboard"),
    path("platform/users/", views.platform_users_view, name="platform-users"),
    path("platform/users/<int:pk>/status/", views.platform_user_status_view, name="platform-user-status"),
    path("platform/coupons/", views.platform_coupons_view, name="platform-coupons"),
    path("platform/dishes/", views.platform_dishes_view, name="platform-dishes"),
    path("platform/dishes/create/", views.platform_dish_create_view, name="platform-dish-create"),
    path("platform/dishes/<int:pk>/", views.platform_dish_update_view, name="platform-dish-update"),
    path("platform/stores/account/", views.platform_store_account_view, name="platform-store-account"),
]

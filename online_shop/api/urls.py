from django.urls import path

from myauth.views import (
    ProfileView,
    UserRegistrationView,
    LogoutAPIView,
    UserLoginView,
    ChangePasswordView,
    UserAvatarUpload,
)

from shopapp.views import (
    TagApiView,
    ProductApiView,
    ProductReviewApiView,
    CategoriesApiView,
    CatalogApiView,
    GetUserForReviewApiView,
    PopularListApiView,
    LimitListApiView,
    BannersListApiView,
    SalesListApiView,
)

from basket.views import BasketApiView
from orders.views import (
    OrderApiView,
    OrderDetailApiView,
    PaymentApiView,
)

app_name = "api"

urlpatterns = [
    path("sign-up/", UserRegistrationView.as_view(), name="sign_up"),
    path("sign-out/", LogoutAPIView.as_view(), name="logout"),
    path("sign-in/", UserLoginView.as_view(), name="sign_in"),
    path("profile/password/", ChangePasswordView.as_view(), name="edit_password"),
    path("profile/avatar/", UserAvatarUpload.as_view(), name="avatar"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("tags/", TagApiView.as_view(), name="tags"),
    path("categories/", CategoriesApiView.as_view(), name="categories"),
    path("catalog/", CatalogApiView.as_view(), name="catalog"),
    path("banners/", BannersListApiView.as_view(), name="banners"),
    path("sales/", SalesListApiView.as_view(), name="sales"),
    path("products/popular/", PopularListApiView.as_view(), name="popular"),
    path("products/limited/", LimitListApiView.as_view(), name="limited"),
    path("product/reviews/", GetUserForReviewApiView.as_view(), name="get_review"),
    path("product/<int:pk>/", ProductApiView.as_view(), name="product_details"),
    path(
        "product/<int:pk>/reviews/",
        ProductReviewApiView.as_view(),
        name="product_reviews",
    ),
    path("basket/", BasketApiView.as_view(), name="basket"),
    path("orders/", OrderApiView.as_view(), name="orders"),
    path("order/<int:pk>/", OrderDetailApiView.as_view(), name="orders_details"),
    path("payment/<int:pk>/", PaymentApiView.as_view(), name="payment"),
]

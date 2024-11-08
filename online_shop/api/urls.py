from django.urls import path

from myauth.views import (
    ProfileView,
    UserRegistrationView,
    LogoutAPIView,
    UserLoginView,
    UserAvatarUpload,
    ChangePasswordView,
)

from shopapp.views import (
    TagApiView,
    ProductApiView,
    ProductReviewApiView,
    CategoriesApiView,
    CatalogApiView,
    GetUserForReviewApiView,
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
    path("product/reviews/", GetUserForReviewApiView.as_view(), name="get_review"),
    path("product/<int:pk>/", ProductApiView.as_view(), name="product_details"),
    path(
        "product/<int:pk>/reviews/",
        ProductReviewApiView.as_view(),
        name="product_reviews",
    ),
]

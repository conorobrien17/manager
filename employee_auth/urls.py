from django.urls import path
from .views import UserDetailView, UserEditView, UserListView, ChangeUserPassword, DepartmentListView, \
    DepartmentCreateView, DepartmentListView, DepartmentDetailView

urlpatterns = [
    path("employees/", UserListView.as_view()),
    path("employees/list", UserListView.as_view(), name="user-list"),
    path("employees/<slug:_slug>/", UserDetailView.as_view(), name="user-detail"),
    path("employees/<slug:_slug/profile", UserDetailView.as_view(), name="user-detail"),
    path("employees/<slug:_slug/edit", UserEditView.as_view(), name="user-edit"),
    path("employees/changepassword", ChangeUserPassword.as_view(), name="user-passwordchange"),
    path("departments/", DepartmentListView.as_view(), name="department-list"),
    path("departments/create", DepartmentCreateView.as_view(), name="department-create"),
    path("departments/list", DepartmentListView.as_view(), name="department-list"),
    path("departments/<int:pk>/detail", DepartmentDetailView.as_view(), name="department-detail"),
]

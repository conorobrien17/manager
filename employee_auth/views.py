from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.views.generic.edit import UpdateView
from .models import User, Department
from .forms import BaseUserEditForm, DepartmentForm
from django.contrib.auth.decorators import permission_required, login_required
from manager.core import paginate_list
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.decorators.cache import never_cache

APP_TEMPLATE_FOLDER = "auth/"
_atf = APP_TEMPLATE_FOLDER
_dtf = APP_TEMPLATE_FOLDER + "department/"
USER_PAGINATE_BY = 15
DEPARTMENT_PAGINATE_BY = 15

edit_decorators = [never_cache, login_required]


@method_decorator(login_required, name="dispatch")
def can_edit_user(request, requested_user_pk):
    """ Check if a user has permission to edit a User object """
    if request.user.has_perm("employee_auth.edit_all_users") or request.user.pk == requested_user_pk:
        return True
    return False


# @permission_required("employee_auth.list_users")
@method_decorator(login_required, name="dispatch")
class UserListView(ListView):
    model = User
    context_object_name = "users"
    template_name = _atf + "user/list.html"
    paginate_by = USER_PAGINATE_BY

    def get_queryset(self):
        return User.objects.order_by("username")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        users = self.get_queryset()
        context["users"] = paginate_list(self, users)
        return context


@method_decorator(edit_decorators, name="dispatch")
class UserDetailView(DetailView):
    model = User
    context_object_name = "profile"
    template_name = _atf + "user/detail.html"

    def get_object(self, queryset=User.objects):
        return queryset.get(pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        requested_pk = self.kwargs.get("pk")
        context["profile"] = User.objects.get(pk=int(requested_pk))
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        return render(request, self.template_name, context)


@method_decorator(edit_decorators, name="dispatch")
class UserEditView(UpdateView):
    model = User
    context_object_name = "user"
    template_name = _atf + "user/edit.html"
    form_class = BaseUserEditForm

    def get_object(self, queryset=User.objects):
        return queryset.get(pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        context["user"] = self.get_object()
        return context

    '''
    def get_form(self, form_class=None):
        if self.request.user.has_perm("employee_auth.edit_all_users"):
            return AdminUserEditFormMixin(instance=self.get_object())
        elif can_edit_user(self.request, self.kwargs.get("pk")):
            return BaseUserEditForm(instance=self.get_object())
        return None
    '''

    def get_success_url(self):
        pk = self.kwargs.get("pk")
        if self.kwargs.get("pk"):
            return reverse_lazy("user-detail", args=[pk])
        else:
            return reverse_lazy("user-list", args=[pk])

    '''
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST)
        pk = self.kwargs.get("pk")
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy("user-detail", args=[pk]))
        return render(request, self.template_name, {"form": form})
    '''


@method_decorator(login_required, name="dispatch")
class ChangeUserPassword(TemplateView):
    model = User
    template_name = _atf + "passwordchange.html"

    def get(self, request, *args, **kwargs):
        form = PasswordChangeForm(self.request.user)
        return render(self.request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(self.request.user, self.request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            update_session_auth_hash(self.request, user)
            messages.success(self.request, "Your password has been successfully changed")
            return HttpResponseRedirect(reverse_lazy("index"))
        else:
            form = PasswordChangeForm(self.request.user)
            messages.error(self.request,
                           "Sorry, but there was an error processing your password change. Please try again.")
            return render(self.request, self.template_name, {"form": form})


@method_decorator(login_required, name="dispatch")
class DepartmentCreateView(CreateView):
    model = Department
    template_name = _dtf + "create.html"

    def get(self, request, *args, **kwargs):
        context = {"form": DepartmentForm()}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save(commit=False)
            department.save()
            return HttpResponseRedirect(reverse_lazy("department-detail", args=[department.pk]))
        return render(request, self.template_name, {"form": form})


@method_decorator(login_required, name="dispatch")
class DepartmentListView(ListView):
    model = Department
    context_object_name = "departments"
    template_name = _dtf + "list.html"
    paginate_by = DEPARTMENT_PAGINATE_BY

    def get_queryset(self):
        return Department.objects.order_by("name")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DepartmentListView, self).get_context_data(**kwargs)
        departments = self.get_queryset()
        context["departments"] = paginate_list(self, departments)
        return context


@method_decorator(login_required, name="dispatch")
class DepartmentDetailView(DetailView):
    model = Department
    context_object_name = "department"
    template_name = _dtf + "detail.html"

    def get_object(self, queryset=Department.objects):
        return queryset.get(pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = int(self.kwargs.get("pk"))
        context["members"] = User.objects.filter(department=pk)
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        return render(request, self.template_name, context)
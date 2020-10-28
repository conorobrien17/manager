from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def paginate_list(self, list_name):
    """
        This function returns a paginated object of the list passed in. The list should generally be a queryset.
    """
    page_ = self.request.GET.get("page", )
    paginator = Paginator(list_name, self.paginate_by)

    try:
        list_name = paginator.page(page_)
    except PageNotAnInteger:
        list_name = paginator.page(1)
    except EmptyPage:
        list_name = paginator.page(paginator.num_pages)
    return list_name
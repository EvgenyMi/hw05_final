from django.core.paginator import Paginator

TOP_TEN = 10


def paginations(request, posts):
    paginator = Paginator(posts, TOP_TEN)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj

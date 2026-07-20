from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """
    Pagination for the offers list, allowing the client to override page size.
    """
    page_size_query_param = 'page_size'

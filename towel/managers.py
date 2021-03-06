import re

from django.db import models
from django.db.models import Q

from towel import queryset_transform

def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


class SearchManager(queryset_transform.TransformManager):
    """
    Stupid searching manager

    Does not use fulltext searching abilities of databases. Constructs a query
    searching specified fields for a freely definable search string. The
    individual terms may be grouped by using apostrophes, and can be prefixed with
    + or - signs to specify different searching modes::

        +django "shop software" -satchmo

    Usage example::

        class MyModelManager(SearchManager):
            search_fields = ('field1', 'name', 'related__field')

        class MyModel(models.Model):
            # ...

            objects = MyModelManager()

        MyModel.objects.search('yeah -no')
    """

    search_fields = ()

    def search(self, query):
        """
        This implementation stupidly forwards to _search, which does the gruntwork.

        Put your customizations in here.
        """

        return self._search(query)

    def _search(self, query):
        queryset = self.get_query_set()

        if not query or not self.search_fields:
            return queryset

        for keyword in normalize_query(query):
            negate = False
            if len(keyword)>1:
                if keyword[0] == '-':
                    keyword = keyword[1:]
                    negate = True
                elif keyword[0] == '+':
                    keyword = keyword[1:]

            if negate:
                q = reduce(lambda p, q: p&q,
                    (~Q(**{'%s__icontains' % field: keyword}) for field in self.search_fields),
                    Q())
            else:
                q = reduce(lambda p, q: p|q,
                    (Q(**{'%s__icontains' % field: keyword}) for field in self.search_fields),
                    Q())

            queryset = queryset.filter(q)

        return queryset

from functools import wraps
from django.core.exceptions import FieldError
from django.db import models, backends
from django.db import connection
from MySQLdb import OperationalError
from MySQLdb.constants.ER import FT_MATCHING_KEY_NOT_FOUND


def _get_indices(model):
    """ Return all of the FULLTEXT indices available for a given
        Django model."""
    
    cursor = connection.cursor()
    cursor.execute('show index from %s where index_type = "FULLTEXT"' %
                   connection.ops.quote_name(model._meta.db_table))
    found = {}
    item = cursor.fetchone()
    while item:
        if not item:
            break
        (model_name, key_name, column_name) = (item[0], item[2], item[4])
        if not found.has_key(key_name):
            found[key_name] = []
        found[key_name].append(column_name)
        item = cursor.fetchone()

    return found.values()


def _handle_oper(f):
    """ Specialized wrapper for methods of SearchQuerySet that will
        inform the user of what indices are available, should the user
        specify a list of fields on which to search."""

    def wrapper(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except OperationalError, e:
            if e.args[0] != FT_MATCHING_KEY_NOT_FOUND:
                raise

            idc = _get_indices(self.model)
            message = "No FULLTEXT indices found for this table."
            if len(idc) > 0:
                message = ("Index not found.  Indices available include: %s" %
                           str(tuple(idc)))
            raise FieldError, message

    return wraps(f)(wrapper)


class SearchQuerySet(models.query.QuerySet):
    """ A QuerySet with a new method, search, and wrappers around the
        most common operations performed on a query set."""

    def __init__(self, model = None, query = None, using = None,
                 aggregate_field_name = 'relevance'):
        
        super(SearchQuerySet, self).__init__(model, query, using)
        self._aggregate_field_name = aggregate_field_name
        

    def search(self, query, fields):
        meta = self.model._meta

        if not fields:
            found = _get_indices(self.model)
            if len(found) != 1:
                raise FieldError, "More than one index found for this table."
            fields = found[0]

        columns = [meta.get_field(name, many_to_many=False).column
                   for name in fields]
        full_names = ["%s.%s" % (connection.ops.quote_name(meta.db_table),
                                 connection.ops.quote_name(column))
                      for column in columns]
        match_expr = "MATCH(%s) AGAINST (%%s)" % (", ".join(full_names))

        return self.extra(select={self._aggregate_field_name: match_expr},
                          where=[match_expr],
                          params=[query],
                          select_params = [query])


    # Python Magic Methods wrapped to provide useful information on exception.

    def __repr__(self):
        return super(SearchQuerySet, self).__repr__()
    __repr__ = _handle_oper(__repr__)

    
    def __len__(self):
        return super(SearchQuerySet, self).__len__()
    __len__ = _handle_oper(__len__)


    def __iter__(self):
        return super(SearchQuerySet, self).__iter__()
    __iter__ = _handle_oper(__iter__)


    def _result_iter(self):
        return super(SearchQuerySet, self)._result_iter()
    _result_iter = _handle_oper(_result_iter)


    def __nonzero__(self):
        return super(SearchQuerySet, self).__nonzero__()
    __nonzero__ = _handle_oper(__nonzero__)


    def __getitem__(self, k):
        return super(SearchQuerySet, self).__getitem__(k)
    __getitem__ = _handle_oper(__getitem__)


    # This is a private method of QuerySet.  It's not guaranteed to even exist
    # after Django 1.2

    def _fill_cache(self, *args, **kwargs):
        return super(SearchQuerySet, self)._fill_cache(*args, **kwargs)
    _fill_cache = _handle_oper(_fill_cache)



class SearchManager(models.Manager):

    def get_query_set(self, fields = []):
        return SearchQuerySet(self.model)


    def search(self, query, fields = []):
        return self.get_query_set().search(query, fields)

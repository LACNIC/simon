import copy
from django.http import Http404
from django.core import paginator
from django.utils.datastructures import SortedDict
from django.utils.encoding import force_unicode, StrAndUnicode
from django.utils.text import capfirst
from columns import Column
from options import options


__all__ = ('BaseTable', 'options')


class TableOptions(object):
    def __init__(self, options=None):
        super(TableOptions, self).__init__()
        self.sortable = getattr(options, 'sortable', None)
        self.order_by = getattr(options, 'order_by', None)


class DeclarativeColumnsMetaclass(type):
    """
    Metaclass that converts Column attributes to a dictionary called
    'base_columns', taking into account parent class 'base_columns'
    as well.
    """
    def __new__(cls, name, bases, attrs, parent_cols_from=None):
        """
        The ``parent_cols_from`` argument determins from which attribute
        we read the columns of a base class that this table might be
        subclassing. This is useful for ``ModelTable`` (and possibly other
        derivatives) which might want to differ between the declared columns
        and others.

        Note that if the attribute specified in ``parent_cols_from`` is not
        found, we fall back to the default (``base_columns``), instead of
        skipping over that base. This makes a table like the following work:

            class MyNewTable(tables.ModelTable, MyNonModelTable):
                pass

        ``MyNewTable`` will be built by the ModelTable metaclass, which will
        call this base with a modified ``parent_cols_from`` argument
        specific to ModelTables. Since ``MyNonModelTable`` is not a
        ModelTable, and thus does not provide that attribute, the columns
        from that base class would otherwise be ignored.
        """

        # extract declared columns
        columns = [(column_name, attrs.pop(column_name))
           for column_name, obj in attrs.items()
           if isinstance(obj, Column)]
        columns.sort(lambda x, y: cmp(x[1].creation_counter,
                                      y[1].creation_counter))

        # If this class is subclassing other tables, add their fields as
        # well. Note that we loop over the bases in *reverse* - this is
        # necessary to preserve the correct order of columns.
        for base in bases[::-1]:
            col_attr = (parent_cols_from and hasattr(base, parent_cols_from)) \
                and parent_cols_from\
                or 'base_columns'
            if hasattr(base, col_attr):
                columns = getattr(base, col_attr).items() + columns
        # Note that we are reusing an existing ``base_columns`` attribute.
        # This is because in certain inheritance cases (mixing normal and
        # ModelTables) this metaclass might be executed twice, and we need
        # to avoid overriding previous data (because we pop() from attrs,
        # the second time around columns might not be registered again).
        # An example would be:
        #    class MyNewTable(MyOldNonModelTable, tables.ModelTable): pass
        if not 'base_columns' in attrs:
            attrs['base_columns'] = SortedDict()
        attrs['base_columns'].update(SortedDict(columns))

        attrs['_meta'] = TableOptions(attrs.get('Meta', None))
        return type.__new__(cls, name, bases, attrs)


def rmprefix(s):
    """Normalize a column name by removing a potential sort prefix"""
    return (s[:1]=='-' and [s[1:]] or [s])[0]

def toggleprefix(s):
    """Remove - prefix is existing, or add if missing."""
    return ((s[:1] == '-') and [s[1:]] or ["-"+s])[0]

class OrderByTuple(tuple, StrAndUnicode):
        """Stores 'order by' instructions; Used to render output in a format
        we understand as input (see __unicode__) - especially useful in
        templates.

        Also supports some functionality to interact with and modify
        the order.
        """
        def __unicode__(self):
            """Output in our input format."""
            return ",".join(self)

        def __contains__(self, name):
            """Determine whether a column is part of this order."""
            for o in self:
                if rmprefix(o) == name:
                    return True
            return False

        def is_reversed(self, name):
            """Returns a bool indicating whether the column is ordered
            reversed, None if it is missing."""
            for o in self:
                if o == '-'+name:
                    return True
            return False
        def is_straight(self, name):
            """The opposite of is_reversed."""
            for o in self:
                if o == name:
                    return True
            return False

        def polarize(self, reverse, names=()):
            """Return a new tuple with the columns from ``names`` set to
            "reversed" (e.g. prefixed with a '-'). Note that the name is
            ambiguous - do not confuse this with ``toggle()``.

            If names is not specified, all columns are reversed. If a
            column name is given that is currently not part of the order,
            it is added.
            """
            prefix = reverse and '-' or ''
            return OrderByTuple(
                    [
                      (
                        # add either untouched, or reversed
                        (names and rmprefix(o) not in names)
                            and [o]
                            or [prefix+rmprefix(o)]
                      )[0]
                    for o in self]
                    +
                    [prefix+name for name in names if not name in self]
            )

        def toggle(self, names=()):
            """Return a new tuple with the columns from ``names`` toggled
            with respect to their "reversed" state. E.g. a '-' prefix will
            be removed is existing, or added if lacking. Do not confuse
            with ``reverse()``.

            If names is not specified, all columns are toggled. If a
            column name is given that is currently not part of the order,
            it is added in non-reverse form."""
            return OrderByTuple(
                    [
                      (
                        # add either untouched, or toggled
                        (names and rmprefix(o) not in names)
                            and [o]
                            or ((o[:1] == '-') and [o[1:]] or ["-"+o])
                      )[0]
                    for o in self]
                    +
                    [name for name in names if not name in self]
            )


class Columns(object):
    """Container for spawning BoundColumns.

    This is bound to a table and provides it's ``columns`` property. It
    provides access to those columns in different ways (iterator,
    item-based, filtered and unfiltered etc)., stuff that would not be
    possible with a simple iterator in the table class.

    Note that when you define your column using a name override, e.g.
    ``author_name = tables.Column(name="author")``, then the column will
    be exposed by this container as "author", not "author_name".
    """
    def __init__(self, table):
        self.table = table
        self._columns = SortedDict()

    def _reset(self):
        """Used by parent table class."""
        self._columns = SortedDict()

    def _spawn_columns(self):
        # (re)build the "_columns" cache of BoundColumn objects (note that
        # ``base_columns`` might have changed since last time); creating
        # BoundColumn instances can be costly, so we reuse existing ones.
        new_columns = SortedDict()
        for decl_name, column in self.table.base_columns.items():
            # take into account name overrides
            exposed_name = column.name or decl_name
            if exposed_name in self._columns:
                new_columns[exposed_name] = self._columns[exposed_name]
            else:
                new_columns[exposed_name] = BoundColumn(self.table, column, decl_name)
        self._columns = new_columns

    def all(self):
        """Iterate through all columns, regardless of visiblity (as
        opposed to ``__iter__``.

        This is used internally a lot.
        """
        self._spawn_columns()
        for column in self._columns.values():
            yield column

    def items(self):
        self._spawn_columns()
        for r in self._columns.items():
            yield r

    def names(self):
        self._spawn_columns()
        for r in self._columns.keys():
            yield r

    def index(self, name):
        self._spawn_columns()
        return self._columns.keyOrder.index(name)

    def sortable(self):
        """Iterate through all sortable columns.

        This is primarily useful in templates, where iterating over the full
        set and checking {% if column.sortable %} can be problematic in
        conjunction with e.g. {{ forloop.last }} (the last column might not
        be the actual last that is rendered).
        """
        for column in self.all():
            if column.sortable:
                yield column

    def __iter__(self):
        """Iterate through all *visible* bound columns.

        This is primarily geared towards table rendering.
        """
        for column in self.all():
            if column.visible:
                yield column

    def __contains__(self, item):
        """Check by both column object and column name."""
        self._spawn_columns()
        if isinstance(item, basestring):
            return item in self.names()
        else:
            return item in self.all()

    def __len__(self):
        self._spawn_columns()
        return len([1 for c in self._columns.values() if c.visible])

    def __getitem__(self, name):
        """Return a column by name."""
        self._spawn_columns()
        return self._columns[name]


class BoundColumn(StrAndUnicode):
    """'Runtime' version of ``Column`` that is bound to a table instance,
    and thus knows about the table's data.

    Note that the name that is passed in tells us how this field is
    delared in the bound table. The column itself can overwrite this name.
    While the overwritten name will be hat mostly counts, we need to
    remember the one used for declaration as well, or we won't know how
    to read a column's value from the source.
    """
    def __init__(self, table, column, name):
        self.table = table
        self.column = column
        self.declared_name = name
        # expose some attributes of the column more directly
        self.visible = column.visible

    @property
    def accessor(self):
        """The key to use when accessing this column's values in the
        source data.
        """
        return self.column.data if self.column.data else self.declared_name

    def _get_sortable(self):
        if self.column.sortable is not None:
            return self.column.sortable
        elif self.table._meta.sortable is not None:
            return self.table._meta.sortable
        else:
            return True   # the default value
    sortable = property(_get_sortable)

    name = property(lambda s: s.column.name or s.declared_name)
    name_reversed = property(lambda s: "-"+s.name)
    def _get_name_toggled(self):
        o = self.table.order_by
        if (not self.name in o) or o.is_reversed(self.name): return self.name
        else: return self.name_reversed
    name_toggled = property(_get_name_toggled)

    is_ordered = property(lambda s: s.name in s.table.order_by)
    is_ordered_reverse = property(lambda s: s.table.order_by.is_reversed(s.name))
    is_ordered_straight = property(lambda s: s.table.order_by.is_straight(s.name))
    order_by = property(lambda s: s.table.order_by.polarize(False, [s.name]))
    order_by_reversed = property(lambda s: s.table.order_by.polarize(True, [s.name]))
    order_by_toggled = property(lambda s: s.table.order_by.toggle([s.name]))

    def get_default(self, row):
        """Since a column's ``default`` property may be a callable, we need
        this function to resolve it when needed.

        Make sure ``row`` is a ``BoundRow`` object, since that is what
        we promise the callable will get.
        """
        if callable(self.column.default):
            return self.column.default(row)
        return self.column.default

    def _get_values(self):
        # TODO: build a list of values used
        pass
    values = property(_get_values)

    def __unicode__(self):
        s = self.column.verbose_name or self.name.replace('_', ' ')
        return capfirst(force_unicode(s))

    def as_html(self):
        pass


class BoundRow(object):
    """Represents a single row of data, bound to a table.

    Tables will spawn these row objects, wrapping around the actual data
    stored in a row.
    """
    def __init__(self, table, data):
        self.table = table
        self.data = data

    def __iter__(self):
        for value in self.values:
            yield value

    def __getitem__(self, name):
        """Returns this row's value for a column. All other access methods,
        e.g. __iter__, lead ultimately to this."""

        column = self.table.columns[name]

        render_func = getattr(self.table, 'render_%s' % name, False)
        if render_func:
            return render_func(self.data)
        else:
            return self._default_render(column)

    def _default_render(self, column):
        """Returns a cell's content. This is used unless the user
        provides a custom ``render_FOO`` method.
        """
        result = self.data[column.accessor]

        # if the field we are pointing to is a callable, remove it
        if callable(result):
            result = result(self)
        return result

    def __contains__(self, item):
        """Check by both row object and column name."""
        if isinstance(item, basestring):
            return item in self.table._columns
        else:
            return item in self

    def _get_values(self):
        for column in self.table.columns:
            yield self[column.name]
    values = property(_get_values)

    def as_html(self):
        pass


class Rows(object):
    """Container for spawning BoundRows.

    This is bound to a table and provides it's ``rows`` property. It
    provides functionality that would not be possible with a simple
    iterator in the table class.
    """

    row_class = BoundRow

    def __init__(self, table):
        self.table = table

    def _reset(self):
        pass   # we currently don't use a cache

    def all(self):
        """Return all rows."""
        for row in self.table.data:
            yield self.row_class(self.table, row)

    def page(self):
        """Return rows on current page (if paginated)."""
        if not hasattr(self.table, 'page'):
            return None
        return iter(self.table.page.object_list)

    def __iter__(self):
        return iter(self.all())

    def __len__(self):
        return len(self.table.data)

    def __getitem__(self, key):
        if isinstance(key, slice):
            result = list()
            for row in self.table.data[key]:
                result.append(self.row_class(self.table, row))
            return result
        elif isinstance(key, int):
            return self.row_class(self.table, self.table.data[key])
        else:
            raise TypeError('Key must be a slice or integer.')


class BaseTable(object):
    """A collection of columns, plus their associated data rows.
    """

    __metaclass__ = DeclarativeColumnsMetaclass

    rows_class = Rows

    # this value is not the same as None. it means 'use the default sort
    # order', which may (or may not) be inherited from the table options.
    # None means 'do not sort the data', ignoring the default.
    DefaultOrder = type('DefaultSortType', (), {})()

    def __init__(self, data, order_by=DefaultOrder):
        """Create a new table instance with the iterable ``data``.

        If ``order_by`` is specified, the data will be sorted accordingly.
        Otherwise, the sort order can be specified in the table options.

        Note that unlike a ``Form``, tables are always bound to data. Also
        unlike a form, the ``columns`` attribute is read-only and returns
        ``BoundColum`` wrappers, similar to the ``BoundField``'s you get
        when iterating over a form. This is because the table iterator
        already yields rows, and we need an attribute via which to expose
        the (visible) set of (bound) columns - ``Table.columns`` is simply
        the perfect fit for this. Instead, ``base_colums`` is copied to
        table instances, so modifying that will not touch the class-wide
        column list.
        """
        self._data = data
        self._snapshot = None      # will store output dataset (ordered...)
        self._rows = self.rows_class(self)
        self._columns = Columns(self)

        # None is a valid order, so we must use DefaultOrder as a flag
        # to fall back to the table sort order. set the attr via the
        # property, to wrap it in an OrderByTuple before being stored
        if order_by != BaseTable.DefaultOrder:
            self.order_by = order_by

        else:
            self.order_by = self._meta.order_by

        # Make a copy so that modifying this will not touch the class
        # definition. Note that this is different from forms, where the
        # copy is made available in a ``fields`` attribute. See the
        # ``Table`` class docstring for more information.
        self.base_columns = copy.deepcopy(type(self).base_columns)

    def _reset_snapshot(self, reason):
        """Called to reset the current snaptshot, for example when
        options change that could affect it.

        ``reason`` is given so that subclasses can decide that a
        given change may not affect their snaptshot.
        """
        self._snapshot = None

    def _build_snapshot(self):
        """Rebuild the table for the current set of options.

        Whenver the table options change, e.g. say a new sort order,
        this method will be asked to regenerate the actual table from
        the linked data source.

        Subclasses should override this.
        """
        return self._data

    def _get_data(self):
        if self._snapshot is None:
            self._snapshot = self._build_snapshot()
        return self._snapshot
    data = property(lambda s: s._get_data())

    def _resolve_sort_directions(self, order_by):
        """Given an ``order_by`` tuple, this will toggle the hyphen-prefixes
        according to each column's ``direction`` option, e.g. it translates
        between the ascending/descending and the straight/reverse terminology.
        """
        result = []
        for inst in order_by:
            if self.columns[rmprefix(inst)].column.direction == Column.DESC:
                inst = toggleprefix(inst)
            result.append(inst)
        return result

    def _cols_to_fields(self, names):
        """Utility function. Given a list of column names (as exposed to
        the user), converts column names to the names we have to use to
        retrieve a column's data from the source.

        Usually, the name used in the table declaration is used for accessing
        the source (while a column can define an alias-like name that will
        be used to refer to it from the "outside"). However, a column can
        override this by giving a specific source field name via ``data``.

        Supports prefixed column names as used e.g. in order_by ("-field").
        """
        result = []
        for ident in names:
            # handle order prefix
            if ident[:1] == '-':
                name = ident[1:]
                prefix = '-'
            else:
                name = ident
                prefix = ''
            # find the field name
            column = self.columns[name]
            result.append(prefix + column.accessor)
        return result

    def _validate_column_name(self, name, purpose):
        """Return True/False, depending on whether the column ``name`` is
        valid for ``purpose``. Used to validate things like ``order_by``
        instructions.

        Can be overridden by subclasses to impose further restrictions.
        """
        if purpose == 'order_by':
            return name in self.columns and\
                   self.columns[name].sortable
        else:
            return True

    def _set_order_by(self, value):
        self._reset_snapshot('order_by')
        # accept both string and tuple instructions
        order_by = (isinstance(value, basestring) \
            and [value.split(',')] \
            or [value])[0]
        if order_by:
            # validate, remove all invalid order instructions
            validated_order_by = []
            for o in order_by:
                if self._validate_column_name(rmprefix(o), "order_by"):
                    validated_order_by.append(o)
                elif not options.IGNORE_INVALID_OPTIONS:
                    raise ValueError('Column name %s is invalid.' % o)
            self._order_by = OrderByTuple(validated_order_by)
        else:
            self._order_by = OrderByTuple()

    order_by = property(lambda s: s._order_by, _set_order_by)

    def __unicode__(self):
        return self.as_html()

    def __iter__(self):
        for row in self.rows:
            yield row

    def __getitem__(self, key):
        return self.rows[key]

    # just to make those readonly
    columns = property(lambda s: s._columns)
    rows = property(lambda s: s._rows)

    def as_html(self):
        pass

    def update(self):
        """Update the table based on it's current options.

        Normally, you won't have to call this method, since the table
        updates itself (it's caches) automatically whenever you change
        any of the properties. However, in some rare cases those
        changes might not be picked up, for example if you manually
        change ``base_columns`` or any of the columns in it.
        """
        self._build_snapshot()

    def paginate(self, klass, *args, **kwargs):
        page = kwargs.pop('page', 1)
        self.paginator = klass(self.rows, *args, **kwargs)
        try:
            self.page = self.paginator.page(page)
        except paginator.InvalidPage, e:
            raise Http404(str(e))

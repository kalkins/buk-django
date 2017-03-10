from django.db import connections
from django.db.utils import ConnectionDoesNotExist, DataError

class ImportSkipRow(Exception):
    pass

# A class for avoiding boilerplate code when importing from another database
class LegacyImporter:
    # The database to import from
    db = 'legacy'

    # Whether to overwrite existing entries or not
    overwrite = False

    # The table to import from. Can be a list.
    #table = ''

    # The model to import to
    #model = None

    # The columns to import from/to, on the form
    #
    #   'newcol': 'oldcol'
    # or
    #   'newcol': ['oldcol1', 'oldcol2']
    #
    # If a list is used, the method 'convert_newcol' must be defined
    #cols = {}

    # The columns (in the new model) to check against when determining
    # whether the object already exists in the database. Not setting this
    # correctly could lead to duplicate entries. Defaults to all
    check = {}

    # The columns (in the old database) to overwrite. This is not
    # necessary if overwrite if True
    update = {}

    # The SQL to execute. This will be generated if not provided
    sql = ''

    # The WHERE part of the query, written in SQL
    where = ''

    def generate_sql(self):
        columns = ''
        for newcol, oldcol in self.cols.items():
            if isinstance(oldcol, str):
                if columns:
                    columns += ', '
                columns += '`%s`' % oldcol
            else:
                for col in oldcol:
                    if columns:
                        columns += ', '
                    columns += '`%s`' % col

        tables = ''
        if isinstance(self.table, str):
            tables = self.table
        else:
            for table in self.table:
                if tables:
                    tables += ', '
                tables += '`%s`' % table

        where = ''
        if self.where:
            if 'where' in self.where or 'WHERE' in self.where:
                where = self.where
            else:
                where = 'WHERE %s' % self.where

        self.sql = 'SELECT %s FROM %s %s' % (columns, tables, where)

    def create_instance(self, params):
        obj, new = self.model.objects.get_or_create(**params)
        if not new and self.update:
            defaults = params.pop('defaults')
            params = {**params, **defaults}
            update = {}
            for col in self.update:
                update[col] = params[col]
            self.model.objects.filter(pk=obj.pk).update(**update)

    def execute(self):
        try:
            self.cursor = connections[self.db].cursor()
        except ConnectionDoesNotExist:
            raise ValueError("Database '%s' does not exist." % db)

        if not self.sql:
            self.generate_sql()
        if not self.check:
            self.check = self.cols.keys()
        if self.overwrite:
            self.update = self.cols

        self.cursor.execute(self.sql)
        for row in self.cursor.fetchall():
            try:
                self.foreach(row)
            except Exception as e:
                print('Error handling row:')
                print(row, end='\n\n')
                raise e

    def foreach(self, row):
        params = {'defaults': {}}
        i = 0
        for newcol, oldcol in self.cols.items():
            if isinstance(oldcol, str):
                val = row[i]
                i += 1
            else:
                val = {}
                for j in range(len(oldcol)):
                    val[oldcol[j]] = row[i+j]
                i += len(oldcol)

            if hasattr(self, 'convert_' + newcol):
                try:
                    try:
                        val = getattr(self, 'convert_' + newcol)(**val)
                    except TypeError as e:
                        if 'mapping' in str(e) or 'unexpected keyword' in str(e):
                            val = getattr(self, 'convert_' + newcol)(val)
                        else:
                            raise e
                except ImportSkipRow:
                    return
            elif not isinstance(oldcol, str):
                raise ValueError(
                        ("Column '%s' is dependent on several columns in the old database, " \
                        +"but no conversion function was provided.") % newcol)

            if newcol in self.check:
                if newcol == 'defaults':
                    newcol = 'defaults__exact'
                params[newcol] = val
            else:
                params['defaults'][newcol] = val

        self.create_instance(params)

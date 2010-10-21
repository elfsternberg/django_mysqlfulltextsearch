django-mysqlfulltextsearch
==============================

django-mysqlfulltextsearch is a simple plug-in for Django that
provides access to MySQL's FULLTEXT INDEX feature available in MySQL
5.0 and up.

Although Django supports the "search" lookup in QuerySet filters
[http://docs.djangoproject.com/en/dev/ref/models/querysets/#search],
the docs specify that you must create the fulltext index yourself.
This variant, inspired by code from a blog entry by Andrew Durdin
[http://www.mercurytide.co.uk/news/article/django-full-text-search/],
includes a return value "relevance," which is the score MySQL awards
to each row returned.  This is a win for small sites that do not need
a heavyweight search solution such as Lucene or Xapian. ("relevance"
is supposed to be a configurable dynamic field name, but I haven't
provided a reliable path to change it yet.)

Along with the updated API, this code provides for index discovery.
If a table has exactly one fulltext index, you can create a
SearchManager without declaring any fields at all, and it will
auto-discover the index on its own.  If you specify a tuple of search
fields for which no corresponding index exists, the returned exception
will include a list of valid indices.



Standard Usage:
---------------

Create the index.  For the model "book" in the app "Books":

    ./manage dbshell
    > CREATE FULLTEXT INDEX book_title on books_book (title, summary)

Or via South:

    def forwards(self, orm):
        db.execute('CREATE FULLTEXT INDEX book_text_index ON books_book (title, summary)')

Using the index:

    from mysqlfulltextsearch import SearchManager
    class Books:
        ...
        objects = SearchManager()

    books = Book.objects.search('The Metamorphosis', ('title', 'summary')).order_by('-relevance')

    > books[0].title
    "The Metamorphosis"
    > books[0].author
    "Franz Kafka"
    > books[0].relevance
    9.4

If there is only one index for the table, the fields do not need to be
specified, the SearchQuerySet object can find it automatically:

    from mysqlfulltextsearch import SearchManager
    class Books:
        ...
        objects = SearchManager()

    books = Book.objects.search('The Metamorphosis').order_by('-relevance')



Tips:
-----
Generating the index is a relatively heavyweight process.  When you
have a few thousand documents, it might be best to load them first,
then generate the index afterward.  



To Do:
-----

-- Easy

Make the "relevance" dynamic field name configurable.


-- Moderate

Provide means for matching against BOOLEAN, NATURAL LANGUAGE, and
QUERY EXPANSION modes.  (Preliminary experiments with this revealed
some... interesting... problems with parameter quotation.)


-- Difficult

Provide means for using a SearchManager to access indices on joined
tables, for example:

    Author.objects.search("The Metamorphosis", "book__title")

-- Insane

Provide for a way to have FULLTEXT search indices specified in a
model's Meta class, and have syncdb or south pick up that information
and do the right thing with it.

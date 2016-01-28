# Getting documents from Legistar

We should have been writing this document from the beginning, so it may be spotty for the first few drafts.

At the core of City Hall Monitor is a set of processes which periodically retrieve data from the City of Chicago's Legistar implementation to update a SQL database with a mirror of the data and upload the associated PDFs to DocumentCloud.org.

The processes are implemented as a series of Django management commands which are run as cronjobs. The order is laid out in `conf/prd/cityhallmonitor.cron`

It should be safe to run this locally, because the code will not upload duplicate PDFs to DocumentCloud. However, that means that running local tests of commands like `pull_pdfs` may not exactly mirror the codepath expected on production. Specifically, some code is only executed when there is no PDF on DocumentCloud, so testing that locally would require carefully deleting one or two PDFs on DocumentCloud and restoring them as part of a test. This makes me think that generally, local developers are best off working from periodic dumps of the production database, and we can try to make that more systematic.

# Leveraging the Document Cloud archive

At least one partner has asked about taking advantage of the documents we've published to Document Cloud. At this time we haven't planned to build any API which would list all available documents, or such, but if you know the Legistar PDF URL, you can query Document Cloud for our "copy" of it.  Use these parameters to a Document Cloud search:

* account: 2212872-knight-lab
* project: "Chicago City Hall Monitor"
* source: (the URL of the PDF, e.g. http://ord.legistar.com/Chicago/attachments/4fc6aad9-98e2-41ff-8a24-22ca5b38d49e.pdf)

We realize now that this is not the correct semantics of 'source,' but now that we've built the archive, I don't know if we'll take the trouble to change it.

Here's an example URL which finds the above URL for a web browser: https://www.documentcloud.org/public/search/account:%20%2212872-knight-lab%22%20project:%20%22Chicago%20City%20Hall%20Monitor%22%20Source:%20%22http://ord.legistar.com/Chicago/attachments/4fc6aad9-98e2-41ff-8a24-22ca5b38d49e.pdf%22

and you should also be able to adapt those parameters to use with the [Document Cloud search API](https://www.documentcloud.org/help/api#search-documents)

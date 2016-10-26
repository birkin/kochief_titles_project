### about

The kochief_titles project started in 2010. It was an early experimentation by a previous programmer with using the software package '[kochief](https://github.com/gsf/kochief)' to relatively easily create a web presentation of newly-cataloged [Brown University Library](https://library.brown.edu) titles, with search and [faceting](https://www.webdesignpractices.com/navigation/facets.html) features.

It's been updated just enough to get into github and work compatibly with a more modern architecture (i.e. passenger vs mod_wsgi).


### solr queries

Solr can be queried through a proxy app. Some examples follow.

- About the examples
    - Some of the example queries are dense, and can be whittled down. That's due to the nature of the app that's designed to communicate with solr.
    - `q` or `q.alt` parameters should be encoded (though some may be shown unencoded below for readability). If playing with queries interactively, the [meyerweb encoder/decoder page](https://meyerweb.com/eric/tools/dencoder/) is your friend.

- [discipline: anthropology](https://library.brown.edu/search/solr_pub/newtitles/?rows=20&facet=true&facet.limit=25&facet.mincount=1&start=0&facet.field=discipline_facet&facet.field=collection_facet&facet.field=building_facet&facet.field=format_facet&facet.field=pubyear_facet&f.pubyear.facet.sort=false&facet.field=language_facet&facet.field=name_facet&facet.field=topic_facet&facet.field=genre_facet&facet.field=language_dubbed_facet&facet.field=language_subtitles_facet&facet.field=place_facet&facet.field=imprint_facet&q.alt=%2A%3A%2A&fq=discipline_facet%3A%22Anthropology%22&sort=accession_date+desc&wt=json&json.nl=arrarr&qt=dismax)
    - with facets, sorted by descending accession_date

- [new-titles for July 2016](https://library.brown.edu/search/solr_pub/newtitles/?q.alt=accession_date:2016-07*&sort=accession_date+desc&wt=json&qt=dismax)
    - no facets, sorted by descending accession_date

- [new-titles for July 01 2016 through July 04 2016](https://library.brown.edu/search/solr_pub/newtitles/?q.alt=accession_date%3A%5B2016-07-01T00%3A00%3A00.000Z%20TO%202016-07-05T00%3A00%3A00.000Z%5D&sort=accession_date+desc&wt=json&qt=dismax)
    - no facets, sorted by descending accession_date
    - that format, unencoded, is like: `accession_date:[2016-07-01T00:00:00.000Z TO 2016-07-05T00:00:00.000Z]`


---

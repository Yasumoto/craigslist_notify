# craigslist_notify.py
If you're searching on craigslist for a apartment in San Francisco, or any
other sought-after item, this script can give you an edge.  It polls a
craigslist RSS feed URL (which is linked at the bottom of craigslist search
and listing pages) and emails you when new postings are found.
If you're crafty, you can have emails sent to your cell carrier's
[SMS gateway](https://en.wikipedia.org/wiki/List_of_SMS_gateways) to receive
a text message for each posting.

## Requirements
* python 2.4+
* python [feedparser module](https://pypi.python.org/pypi/feedparser)

## Usage
```
$ python rss_notify.py             \
    -f $FEEDURL                    \
    -e $TO_EMAILS                  \
    --smtp_auth_user $FROM_EMAIL   \
    --smtp_auth_pass $SMTP_PASS    \
    --smtp_server $SMTP_SERVER     \
    --smtp_server_port $SMTP_PORT
```

You may also provide a comma-delimited list of ```--filters``` to omit postings
containing specific strings.

## Tips
* If apartment hunting in San Francisco, filter ```TMS333```, which seems to be
the tagline for a particularly spammy apartment chain.
* For gmail's SMTP, use
```--smtp_server smtp.gmail.com --smtp_server_port 587``` along with your
gmail address (e.g. ```--smtp_auth_user myusername@gmail.com```) and password.

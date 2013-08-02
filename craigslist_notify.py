#!/usr/bin/env python

import email.utils
from email.mime.text import MIMEText
import feedparser
from optparse import OptionParser
import smtplib
import sys
import time

options = None

def fetchFeed(url):
  print 'Fetching feed %s' % url
  feed = feedparser.parse(url)
  return feed

def sendMsg(msg):
  if not options.smtp_server or not options.smtp_port or not options.to_emails:
    print ('If SMTP options were configured, '
           'the following message would be sent:')
    print msg.as_string()
    return

  if options.smtp_server:
    srv = smtplib.SMTP(options.smtp_server, options.smtp_port)
  else:
    srv = smtplib.SMTP()
  srv.set_debuglevel(1)

  srv.ehlo()
  srv.starttls()
  srv.ehlo()

  if not options.smtp_user or not options.smtp_pass:
    print 'SMTP auth options not provided, not authenticating'
  else:
    srv.login(options.smtp_user, options.smtp_pass)

  to_emails = options.to_emails.split(',')

  try:
    srv.sendmail(options.from_email, to_emails, msg.as_string())
  finally:
    srv.quit()

def buildMsg(subject, body):
  to_emails = options.to_emails.split(',')

  msg = MIMEText(body)
  msg['To'] = email.utils.formataddr(('', to_emails[0]))
  msg['From'] = email.utils.formataddr(('', options.from_email))
  msg['Subject'] = subject
  return msg

def notify(posts):
  if not posts:
    return
  message_contents = ''
  for post in posts:
    message_contents += '%s: %s\n' % (post['title_detail']['value'], post['link'])
  sendMsg(buildMsg('New Craigslist posts', message_contents))

def prepareArgs(argv):
  parser = OptionParser()
  parser.add_option('-f', '--feeds', action='store',
      type='string', dest='feed_urls')
  parser.add_option('-e', '--to_emails', action='store',
      type='string', dest='to_emails')
  parser.add_option('--from_email', action='store',
      type='string', dest='from_email')
  parser.add_option('-i', '--interval_minutes', action='store',
      type='int', default=10, dest='interval_mins')
  parser.add_option('--smtp_server', action='store',
      type='string', dest='smtp_server')
  parser.add_option('--smtp_server_port', action='store',
      type='int', dest='smtp_port')
  parser.add_option('--smtp_auth_user', action='store',
      type='string', dest='smtp_user')
  parser.add_option('--smtp_auth_pass', action='store',
      type='string', dest='smtp_pass')
  parser.add_option('--filters', action='store',
      type='string', dest='filters')
  (options, args) = parser.parse_args(argv)  
  return options

def main(argv):
  global options
  options = prepareArgs(argv)
  if not options.feed_urls:
    print 'At least one feed must be specified.'
    return
  feed_urls = options.feed_urls.split(',')

  firstScan = True

  # Keeps track of the URLs of postings that we've already
  # sent notifications for.
  posts_seen = []

  # Run forever.
  while True:
    # Notifications to send in this run.
    new_posts = []
    
    # Check each feed.
    for feed in feed_urls:
      feed_data = fetchFeed(feed)
      posts = feed_data['entries']
      if not posts:
        print 'No posting entries were found!'
      else:
        # Check each post in this feed.
        for post in posts:
          if firstScan:
            posts_seen.append(post['link'])
            continue
          
          # Check if we've already seen this post.
          if post['link'] not in posts_seen:
            # Check if the post is filtered.
            for filter_str in options.filters.split(','):
              if filter_str in post['description']:
                print ('Filtering message %s, matches filter %s' %
                    (post['link'], filter_str))
              else:
                new_posts.append(post)

            posts_seen.append(post['link'])

          else:
            print 'Already sent notification for %s' % post['link']

    firstScan = False

    # Send the notification.
    notify(new_posts)

    print 'Sleeping for %d minutes' % options.interval_mins
    time.sleep(options.interval_mins * 60)


if __name__ == '__main__':
	main(sys.argv[1:])

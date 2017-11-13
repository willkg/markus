================
Metrics overview
================

This chapter covers the different types of metrics and what they're useful for.


Counters (incr)
===============

Counters are for counting things. They answers questions like:

* How many requests did my app handle in the last hour?
* How many times did my app rate limit a request?
* How many bytes did my app upload?

Metrics analysis tools (Datadog, Graphite, Grafana, and so on) can also look
counters during periods of time also known as a rate. With tools like that, you
can answer questions like:

* How many requests does my app handle per minute?


Reporting sizes and measures (gauge)
====================================

When you want to measure something over time, you use a gauge. They answer
questions like:

* How much memory does my app use?
* How many items are in the crashmover queue?
* How many threads are running?

Measuring these once isn't interesting. Measuring these periodically and then
seeing those measures go up and down over time and possibly in response to
various events (sudden high load, external service going down, and so on) is
very interesting.

These numbers are useful for monitoring and alerting. For example, maybe when
the crashmover queue hits a specified threshold, that means the app is in
trouble. That's something you'd want to get alerted to.


Getting statistical distributions (timing, histogram)
=====================================================

When you want to measure something over time, but you want statistical
information about those values, you want to use timing and histogram.

Statsd-type monitoring tools will calculate the count, average, median, 95th
percentile, and max for these values over some period.

This helps you answer questions like:

* What's the median, 95%, and max HTTP request payload sizes?
* What's the median and 95% durations for executing some database query?

In these cases, knowing just the measured values isn't helpful, but knowing the
median and 95% is very helpful. You'd be able to see how those things generally
are and what the extreme cases are like.

Some backends don't support histogram. In that case, histograms are reported as
timings because the two are essentially the same where "histogram" is the more
general of the two.


Stats
=====

Depending on the backend you're using, there may be rules for the metrics stats
names you're generating.

Generally, if you follow these rules, your stats should work across all
backends:

1. Use only ASCII letters, ASCII numbers, and periods.
2. The metric stats name should begin with a letter.
3. Keep metric stats names short.


Using tags
==========

Tags give context to a metric. Monitoring tools can show you values, but then
break down the values by tag value. This makes it easier to answer questions
like:

* What's the total number of requests handled by the cluster? Broken down by
  host?
* What's the total number of requests to the site? Broken down by browser?
* What's the total number of throttle requests? Broken down by throttle result?

Tags consist of two parts: a key and a value.

Depending on the backend you're using, there may be rules for the tag names and
values you're using.

Generally, if you follow these rules, your tags should work across all backends:

1. Use only ASCII letters, ASCII numbers, underscores, hyphens, and periods in
   tag names.
2. Tag names should begin with a letter.
3. Tag names should be short.
4. Tag values should be limited to a small (under 1,000) set of possible values.
   Be wary of using ip addresses, usernames, and other things that can have many
   values.

To help with that, use :py:func:`markus.utils.generate_tag` which will sanitize
tags and key/val tags for use with all Markus backends.

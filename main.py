#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.cloud import error_reporting
from google.cloud import logging

from analysis import Analysis
from trading import Trading
from twitter import Twitter


def twitter_callback(text, link):
    """Analyzes Trump tweets, makes stock trades, and sends tweet alerts."""

    # Initialize these here to create separate httplib2 instances per thread.
    analysis = Analysis()
    trading = Trading()

    companies = analysis.find_companies(text)
    logger.log_text("Using companies: %s" % companies, severity="DEBUG")
    if companies:
        trading.make_trades(companies)
        twitter.tweet(companies, link)

if __name__ == "__main__":
    logger = logging.Client(use_gax=False).logger("main")
    error_client = error_reporting.Client()

    # Restart in a loop if there are any errors so we stay up.
    while True:
        logger.log_text("Starting new session.", severity="INFO")

        twitter = Twitter(twitter_callback)
        try:
            twitter.start_streaming()
        except BaseException as exception:
            error_client.report_exception()
            logger.log_text("Exception on main thread: %s" % exception,
                            severity="ERROR")
        finally:
            logger.log_text("Ending session.", severity="INFO")

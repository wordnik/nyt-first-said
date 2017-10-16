# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
"""
import twitter

def TwitterApi():
    return twitter.Api(consumer_key='[consumer key]',
                consumer_secret='[consumer secret]',
                access_token_key='[access token]',
                access_token_secret='[access token secret]')

#!/usr/bin/env python

import urllib, urllib2, cookielib
import re
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

USERNAME = 'admin'
PASSWORD = ''

# 1. Login
# POST to: http://iccaonline.net/amember/admin/index.php

url = 'http://iccaonline.net/amember/admin/index.php'
data = 'passwd=%s&login=%s&do_login=1' % (PASSWORD, USERNAME)
req = urllib2.Request(url, data)
response = opener.open(req)

if "PHPSESSID" in response.read():
    print("Login successful!\n")
else:
    print("Login failed!")
    quit()


# 2. Enter POST loop

# Add Member
# http://iccaonline.net/amember/admin/users.php?action=add_form
# POST to: /amember/admin/users.php
url = 'http://iccaonline.net/amember/admin/users.php'
data = {
    'member_id': '',
    'login': 'testtest',
    'pass': 'testtest',
    'email': 'test@test.com',
    'name_f': 'Testy',
    'name_l': 'McTestington',
    'country': 'US',
    'street': '123 Test St.',
    'city': 'Testington',
    'state': 'TX',
    'zip': '12345',
    'phone': '1234567890',

    'unsubscribed': '0',
    'aff_param': '',
    'action': 'add_save'
}
req = urllib2.Request(url, urllib.urlencode(data))
response = opener.open(req)

html = response.read()
if 'please choose another username' in html:
    print("Error! Username '%s' already taken!" % data['login'])
else:
    print("User '%s' successfully registered!" % data['login'])

    member_id = re.search('member_id=(\d{1,5})', html).group(1)
    print("Member ID: %s" % member_id)

    # Add Subscription
    # http://iccaonline.net/amember/admin/users.php?member_id=131&action=payment
    # POST to: /amember/admin/users.php
    url = 'http://iccaonline.net/amember/admin/users.php'
    data = {
        'receipt_id': 'manual',
        'amount': '0',
        'completed': '1',
        'payment_id': '',
        'member_id': member_id,
        'action': 'payment_add'
    }
    req = urllib2.Request(url, urllib.urlencode(data))
    response = opener.open(req)

    print('\n'+response.read())


# 3. Logout
# GET to: http://iccaonline.net/amember/admin/logout.php

url = 'http://iccaonline.net/amember/admin/logout.php'
response = opener.open(url)

if "Logged out" in response.read():
    print("\nLogged out!")
else:
    print("\nError logging out!")

#!/usr/bin/env python

import urllib, urllib2, cookielib
import datetime, re
import string, random # for password generation

class Error(Exception):
    """ Base class for exceptions in this module. """
    def __init__(self, value):
        self.value = value

class LoginError(Error):
    """ Raised when a login operation fails. """
    def __str__(self):
        return repr("Error logging in as %s" % self.value)

class UserExistsError(Error):
    """ Raised when trying to create a username that already exists in the system. """
    def __str__(self):
        return repr("User '%s' already exists!" % self.value)

class UserUpdateError(Error):
    """ Raised when an error occurs in trying to update existing user information. """
    def __str__(self):
        return repr("Could not update user info for user '%s'!" % self.value)

class AmemberSession(object):
    """ An aMember Session """

    def __init__(self, url, username, password):
        self.url = url # TODO: add logic to chomp off trailing '/'.. make sure /admin/ in url..
        self.username = username
        self.password = password
        
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        self.__login()

    def __del__(self):
        self.__logout()

    def __login(self):
        """ Log in to aMember """

        url = '%s/index.php' % self.url
        data = {
            'login': self.username,
            'passwd': self.password,
            'do_login': '1',
        }
        request = urllib2.Request(url, urllib.urlencode(data))
        response = self.opener.open(request)

        # Raise an exception if login fails.
        if "PHPSESSID" not in response.read():
            raise LoginError(self.username)

    def __logout(self):
        """ Log out of aMember """

        url = '%s/logout.php' % self.url
        response = self.opener.open(url)

    def add_user(self, first_name, last_name, email, phone, street, city, state, zipcode, country='US', username=None):
        """ Add a user to aMember """

        if username is None:
            username = ''.join([first_name[0].lower(), last_name.lower()])
        password = self.__generate_password(10)

        url = '%s/users.php' % self.url
        data = {
            'member_id': '',
            'login': username,
            'pass': password,
            'email': email,
            'name_f': first_name,
            'name_l': last_name,
            'country': country,
            'street': street,
            'city': city,
            'state': state,
            'zip': zipcode,
            'phone': phone,
        }
        extra = {
            'unsubscribed': '0',
            'aff_param': '',
            'action': 'add_save'
        }
        request = urllib2.Request(url, urllib.urlencode(dict(data.items() + extra.items())))
        response = self.opener.open(request)

        try:
            # Raise an exception if the username already exists in aMember.
            html = response.read()
            if 'please choose another username' in html:
                raise UserExistsError(username)
            else:
                data['member_id'] = re.search('member_id=(\d{1,5})', html).group(1)
                return data

        except UserExistsError:
            try:
                num = int(re.search(r'^(.*)(\d+)$', username).group(2))
                num += 1
                username = re.search(r'^(.*)(\d+)$', username).group(1)
            except AttributeError:
                num = 1

            username = username+str(num)
            return self.add_user(first_name, last_name, email, phone, street, city, state, zipcode, country, username)

    def __generate_password(self, length):
        """ Generate a random password of a given length. """

        s = string.lowercase + string.uppercase + string.digits
        return ''.join(random.choice(s) for i in range(length))

    def del_user(self, member_id):
        """ Remove a user from aMember based on the member_id """

        url = '%s/users.php' % self.url
        data = {
            'member_id': member_id,
            'action': 'delete',
            'confirm': ' Yes ',
        }
        response = self.opener.open(url, urllib.urlencode(data))

    def add_subscription(self, member_id, product_id, start_date, end_date):
        """ Add a subscription to a given member. """

        url = '%s/users.php' % self.url
        data = {
            'member_id': member_id,
            'product_id': product_id,
            'begin_dateMonth': str(start_date.month).rjust(2,'0'),
            'begin_dateDay': str(start_date.day).rjust(2,'0'),
            'begin_dateYear': str(start_date.year),
            'expire_dateMonth': str(end_date.month).rjust(2,'0'),
            'expire_dateDay': str(end_date.day).rjust(2,'0'),
            'expire_dateYear': str(end_date.year),
        }
        extra = {
            'receipt_id': 'manual',
            'paysys_id': 'free',
            'amount': '0',
            'completed': '1',
            'payment_id': '',
            'action': 'payment_add',
        }
        request = urllib2.Request(url, urllib.urlencode(dict(data.items() + extra.items())))
        response = self.opener.open(request)

        if "Member Info Updated" not in response.read():
            raise UserUpdateError(member_id)


if __name__ == '__main__':
    print("Logging in..")
    a = AmemberSession('http://iccaonline.net/amember/admin', 'admin', 'password')

    #for i in range(188,258):
    #    print("Deleting user: "+str(i))
    #    a.del_user(i)
    #quit()

    import csv

    data = csv.DictReader(open('premium-errors.csv', 'rb'))
    output = csv.writer(open('premium-done.csv', 'wa'))
    output.writerow(['first_name','last_name','email','member_id','username','password','level'])

    for p in data:
        print("Creating user for %s %s" % (p['first_name'], p['last_name']))
        m = a.add_user(
            p['first_name'].strip(),
            p['last_name'].strip(),
            p['email'].strip(),
            p['phone'].strip(),
            p['street'].strip(),
            p['city'].strip(),
            p['state'].strip(),
            p['zipcode'].strip()
        )

        product_id = 2 # ICCA Premium Charter Member
        start_date = datetime.date.today()
        end_date = start_date.replace(year=start_date.year+1)

        print("Adding subscription for %s" % m['login'])
        a.add_subscription(m['member_id'], product_id, start_date, end_date)

        output.writerow([
            p['first_name'],
            p['last_name'],
            p['email'],
            m['member_id'],
            m['login'],
            m['pass'],
            p['level'],
        ])

        print("[+] Added User: %s (%s). Password: '%s'." % (m['login'], m['member_id'], m['pass']))

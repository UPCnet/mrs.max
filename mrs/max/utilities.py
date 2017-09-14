from five import grok
from zope.interface import Interface
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility

from maxclient.rest import MaxClient
from hubclient import HubClient
from mrs.max.browser.controlpanel import IMAXUISettings

from plone import api

import logging
from pprint import pformat
import json

logger = logging.getLogger('mrs.max')


class IMAXClient(Interface):
    """ Marker for MaxClient global utility """


class IHubClient(Interface):
    """ Marker for HubClient global utility """


class MAXClient(object):
    """ The utility will return a tuple with the settings and an instance of a
        MaxClient (REST-ish) object.
    """
    grok.implements(IMAXClient)

    def __init__(self):
        self._conn = None

    def __call__(self):
        return self.connection

    def create_new_connection(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IMAXUISettings, check=False)
        logger.info('New MAX connection from domain: {}'.format(settings.domain))
        self._conn = (MaxClient(url=settings.max_server, oauth_server=settings.oauth_server), settings)

    @property
    def connection(self):
        self.create_new_connection()
        return self._conn


grok.global_utility(MAXClient)


class HUBClient(object):
    """ The utility will return a tuple with the settings and an instance of a
        HubClient (REST-ish) object.
    """
    grok.implements(IHubClient)

    def __init__(self):
        self._conn = None

    def __call__(self):
        return self.connection

    def create_new_connection(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IMAXUISettings, check=False)
        logger.info('New HUB connection from domain: {}'.format(settings.domain))
        self._conn = (HubClient(settings.domain, settings.hub_server, expand_underscores=False), settings)

    @property
    def connection(self):
        self.create_new_connection()
        return self._conn


grok.global_utility(HUBClient)


def set_user_oauth_token(user, token):
    member = api.user.get(username=user)
    member.setMemberProperties({'oauth_token': token})


def prettyResponse(response):
    message = ''
    try:
        json_response = json.loads(response)
        message = pformat(json_response)
    except:
        message = response
    return message

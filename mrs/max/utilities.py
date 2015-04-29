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


class max_client_utility(object):
    """ The utility will return a tuple with the settins and an instance of a
        MaxClient (REST-ish) object.
    """
    grok.implements(IMAXClient)

    def __call__(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IMAXUISettings, check=False)
        return (MaxClient(url=settings.max_server, oauth_server=settings.oauth_server),
                settings)

grok.global_utility(max_client_utility)


class hub_client_utility(object):
    """ The utility will return a tuple with the settins and an instance of a
        HubClient (REST-ish) object.
    """
    grok.implements(IHubClient)

    def __call__(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IMAXUISettings, check=False)
        return (HubClient(settings.domain, settings.hub_server, expand_underscores=False),
                settings)

grok.global_utility(hub_client_utility)


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

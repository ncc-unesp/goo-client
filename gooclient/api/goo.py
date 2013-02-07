#!/usr/bin/env python
# This code is based on slumber, but dont uses requests.
# Now we are using pure urllib2.

import urllib2
import urllib
import urlparse
import posixpath
from gooclient.api.exceptions import *
from gooclient.api.serialize import Serializer


class RequestWithMethod(urllib2.Request):
    def __init__(self, method, *args, **kwargs):
        self._method = method
        urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        return self._method

class ResourceCommon(object):

    def _url_join(self, base, *args):
        """
        Helper function to join an arbitrary number of url segments together.
        """
        scheme, netloc, path, query, fragment = urlparse.urlsplit(base)
        path = path if len(path) else "/"
        path = posixpath.join(path, *[('%s' % x) for x in args])
        return urlparse.urlunsplit([scheme, netloc, path, query, fragment])

    def __getattr__(self, item):
        if item.startswith("_"):
            raise AttributeError(item)

        kwargs = {}
        for key, value in self._store.iteritems():
            kwargs[key] = value

        kwargs.update({"base_url": self._url_join(self._store["base_url"], item)})

        return Resource(**kwargs)

class Resource(ResourceCommon, object):
    def __init__(self, *args, **kwargs):
        self._store = kwargs

    def __call__(self, id=None):
        """
        Returns a new instance of self modified by one or more of the available
        parameters. These allows us to do things like override format for a
        specific request, and enables the api.resource(ID).get() syntax to get
        a specific resource by it's ID.
        """

        # Short Circuit out if the call is empty
        if id is None:
            return self

        kwargs = {}
        for key, value in self._store.iteritems():
            kwargs[key] = value

        if id is not None:
            kwargs["base_url"] = self._url_join(self._store["base_url"], id)

        kwargs["session"] = self._store["session"]

        return self.__class__(**kwargs)

    def _print_debug(self, *args, **kwargs):
        if self._store["debug"]:
            print "DEBUG ",
            print kwargs['fmt'] % args

    def _debug(self, response, request):
        # Debug request
        self._print_debug(request._method,
                          request._Request__original,
                          fmt=">> %s %s")
        for k,v in request.headers.items():
            self._print_debug(k,v, fmt=">> %s: %s")

        self._print_debug(request.data, fmt=">> %s")

        # Debug responseonse
        status = response.code
        reason = response.msg
        self._print_debug(status, reason, fmt="<< %s %s")
        for k,v in response.headers.items():
            self._print_debug(k,v, fmt="<< %s: %s")

    def _request(self, method, data=None, params=None, files=None):
        url = self._store["base_url"]

        if self._store["append_slash"] and not url.endswith("/"):
            url += "/"

        if params:
            url += '?' + urllib.urlencode(params)

        request = RequestWithMethod(method = method, url = url)
        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            raise HttpClientError("Client Error %s: %s" % (e.code, e.url), content=e.msg)
        except urllib2.URLError as e:
            raise HttpServerError("Server Error %s" % (e.reason))
        else:

            self._debug(response, request)

            self._ = response
            return response

    def _try_to_serialize_response(self, resp):

        s = self._store["serializer"]

        if resp.headers.get("content-type", None):
            content_type = resp.headers.get("content-type").split(";")[0].strip()

            try:
                stype = s.get_serializer(content_type=content_type)
            except exceptions.SerializerNotAvailable:
                return resp.read()

            return stype.loads(resp.read())
        else:
            return resp.read()

    def get(self, **kwargs):
        response = self._request("GET", params=kwargs)
        if 200 <= response.code <= 299:
            return self._try_to_serialize_response(response)

        return None


class GooAPI(ResourceCommon, object):
    def __init__(self, base_url=None, auth=None, format=None, append_slash=True, serializer=None, session=None, debug=False):
        if serializer is None:
            s = Serializer(default=format)

        self._store = {
            "base_url": base_url,
            "format": format if format is not None else "json",
            "append_slash": append_slash,
            "debug": debug,
            "serializer": s,
        }

        # Do some Checks for Required Values
        if self._store.get("base_url") is None:
            print "base_url is required"

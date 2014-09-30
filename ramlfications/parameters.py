#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Spotify AB


HTTP_METHODS = ["get", "post", "put", "delete", "patch", "options", "head"]


class ContentType(object):
    def __init__(self, name, schema, example):
        self.name = name
        self.schema = schema
        self.example = example


class BaseParameter(object):
    """
    Base parameter with properties defined by the RAML spec's
    'Named Paramters' section.
    """
    def __init__(self, item, data, param_type):
        self.item = item
        self.data = data
        self.param_type = param_type

    @property
    def name(self):
        """Name of the {0}""".format(self.param_type)
        return self.item

    @property
    def display_name(self):
        """Display Name of the {0}""".format(self.param_type)
        return self.data.get('displayName')

    @property
    def type(self):
        """Type of {0}""".format(self.param_type)
        return self.data.get('type')

    @property
    def description(self):
        """Description of {0}""".format(self.param_type)
        return self.data.get('description')

    @property
    def example(self):
        """Example of {0}""".format(self.param_type)
        return self.data.get('example', '')

    @property
    def enum(self):
        """Enum of {0}""".format(self.param_type)
        return self.data.get('enum')

    @property
    def default(self):
        return self.data.get('default')

    @property
    def pattern(self):
        # TODO: what does pattern give me?
        return self.data.get('pattern')

    @property
    def min_length(self):
        # TODO: set for only "string" types
        return self.data.get('minLength')

    @property
    def max_length(self):
        # TODO: set for only "string" types
        return self.data.get('maxLength')

    @property
    def minimum(self):
        # TODO: set for only integer/number types
        return self.data.get('minimum')

    @property
    def maximum(self):
        # TODO: set for only integer/number types
        return self.data.get('maximum')

    @property
    def repeat(self):
        return self.data.get('repeat')


class JSONFormParameter(object):   # pragma: no cover
    def __init__(self, param, data, example):
        self.item = param
        self.data = data
        self.param_type = 'JSON Parameter'
        super(BaseParameter, self).__init__()
        self.example = example

    @property
    def required(self):
        return self.data.get('required')


class URIParameter(BaseParameter):
    def __init__(self, param, data, required=True):
        self.item = param
        self.data = data
        self.param_type = 'URI Parameter'
        super(BaseParameter, self).__init__()
        self.required = required


class QueryParameter(BaseParameter):
    def __init__(self, param, data):
        self.item = param
        self.data = data
        self.param_type = 'Query Parameter'
        super(BaseParameter, self).__init__()

    @property
    def required(self):
        return self.data.get('required')


class FormParameter(BaseParameter):
    def __init__(self, param, data):
        self.item = param
        self.data = data
        self.param_type = 'Form Parameter'
        super(BaseParameter, self).__init__()

    @property
    def required(self):
        return self.data.get('required')


class Header(BaseParameter):
    def __init__(self, name, data, method):
        self.item = name
        self.data = data
        self.param_type = "Header"
        super(BaseParameter, self).__init__()
        self.method = method


class Response(object):
    def __init__(self, code, data, method):
        self.code = code
        self.data = data
        self.method = method
        self.param_type = "Response"

    @property
    def description(self):
        return self.data.get('description')

    @property
    def headers(self):
        _headers = self.data.get('headers')
        headers = []
        if _headers:
            for k, v in list(_headers.items()):
                headers.append(Header(k, v, self.method))
        return headers

    @property
    def body(self):
        return self.data.get('body')

    @property
    def resp_content_types(self):
        content_type = []
        if self.data.get('body'):
            # grabs all content types
            content_types = self.data.get('body')
            types = self.data.get('body').keys()
            for content in types:
                schema = content_types.get(content).get('schema')
                example = content_types.get(content).get('example')
                content_type.append(ContentType(content, schema, example))
        return content_type


class ResourceType(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @property
    def usage(self):
        return self.data.get('usage')

    @property
    def description(self):
        return self.data.get('description')

    @property
    def type(self):
        return self.data.get('type')

    @property
    def methods(self):
        methods = []
        for m in HTTP_METHODS:
            if self.data.get(m):
                rec = ResourceTypeMethod(m, self.data.get(m))
                methods.append(rec)
            elif self.data.get(m + "?"):
                rec = ResourceTypeMethod(m + "?", self.data.get(m + "?"))
                methods.append(rec)
        return methods


class ResourceTypeMethod(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @property
    def optional(self):
        return "?" in self.name


class Documentation(object):
    # TODO: parse markdown content
    def __init__(self, title, content):
        self.title = title
        self.content = content


class SecuritySchemes(object):
    def __init__(self, raml_file):
        self.raml = raml_file

    def _get_security_schemes(self):
        defined_schemes = self.raml.get('securitySchemes')
        if defined_schemes:
            schemes = []
            for scheme in defined_schemes:
                for k, v in list(scheme.items()):
                    schemes.append(SecurityScheme(k, v))
            return schemes
        else:
            return None

    @property
    def security_schemes(self):
        return self._get_security_schemes()


class SecurityScheme(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @property
    def type(self):
        return self.data.get('type')

    @property
    def described_by(self):
        _described_by = self.data.get('describedBy')

        if _described_by:
            described_by = {}

            _headers = _described_by.get('headers')
            _responses = _described_by.get('responses')
            _q_params = _described_by.get('queryParameters')
            _u_params = _described_by.get('uriParameters')
            _f_params = _described_by.get('formParameters')

            if _headers:
                head = []
                for k, v in list(_headers.items()):
                    head.append(Header(k, v, method=None))
                described_by['headers'] = head

            if _responses:
                resp = []
                for k, v in list(_responses.items()):
                    resp.append(Response(k, v, method=None))
                described_by['responses'] = resp

            if _q_params:
                q = []
                for k, v in list(_q_params.items()):
                    q.append(QueryParameter(k, v))
                described_by['query_parameters'] = q

            if _u_params:
                u = []
                for k, v in list(_u_params.items()):
                    u.append(URIParameter(k, v))
                described_by['uri_parameters'] = u

            if _f_params:
                f = []
                for k, v in list(_f_params.items()):
                    f.append(FormParameter(k, v))
                described_by['form_parameters'] = f

            return described_by
        return None

    @property
    def description(self):
        return self.data.get('description')

    def _get_oauth_scheme(self, scheme):
        return {'oauth_2_0': Oauth2Scheme,
                'oauth_1_0': Oauth1Scheme}[scheme]

    @property
    def settings(self):
        schemes = ['oauth_2_0', 'oauth_1_0']
        if self.name in schemes:
            return self._get_oauth_scheme(self.name)(self.data.get('settings'))


class Oauth2Scheme(object):
    def __init__(self, settings):
        self.settings = settings

    @property
    def scopes(self):
        return self.settings.get('scopes')  # list of strings

    @property
    def authorization_uri(self):
        return self.settings.get('authorizationUri')  # string

    @property
    def access_token_uri(self):
        return self.settings.get('accessTokenUri')  # string

    @property
    def authorization_grants(self):
        return self.settings.get('authorizationGrants')  # list of strings


class Oauth1Scheme(object):
    def __init__(self, settings):
        self.settings = settings

    @property
    def request_token_uri(self):
        return self.settings.get('requestTokenUri')

    @property
    def authorization_uri(self):
        return self.settings.get('authorizationUri')

    @property
    def token_credentials_uri(self):
        return self.settings.get('tokenCredentialsUri')
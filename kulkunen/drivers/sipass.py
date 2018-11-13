import requests
import jsonschema
from datetime import datetime, timedelta
from contextlib import contextmanager

from .base import AccessControlDriver, ImproperlyConfigured


ACCESS_RULE_TYPES = {
    'access_point_group': 1,
    'access_point': 2,
    'access_level': 3,
    'access_group': 4,
    'venue_booking': 12,
}

DEFAULT_TIME_SCHEDULE_ID = '1'  # Usually (?) maps to "Always"


class UnauthorizedError(Exception):
    pass


class SiPassAccessRule:
    def __init__(self, target, start_time=None, end_time=None,
                 time_schedule_id=DEFAULT_TIME_SCHEDULE_ID):
        self.target = target
        self.start_time = start_time
        self.end_time = end_time
        self.type = ACCESS_RULE_TYPES[target['type']]
        self.time_schedule_id = time_schedule_id


class SiPassToken:
    value: str
    expires_at: datetime

    def __init__(self, value, expires_at):
        self.value = value
        self.expires_at = expires_at

    def has_expired(self):
        if self.expires_at is None:
            return False
        now = datetime.now()
        if now > self.expires_at + timedelta(seconds=30):
            return True
        return False

    def refresh(self, expiration_time):
        self.expires_at = datetime.now() + timedelta(seconds=expiration_time)

    def serialize(self):
        return dict(value=self.value, expires_at=self.expires_at.timestamp())

    @classmethod
    def deserialize(cls, data):
        try:
            value = data['value']
            expires_at = datetime.fromtimestamp(data['expires_at'])
        except Exception:
            return None
        return SiPassToken(value=value, expires_at=expires_at)


class SiPassDriver(AccessControlDriver):
    token: SiPassToken
    token_expiration_time: int

    SYSTEM_CONFIG_SCHEMA = {
        "type": "object",
        "properties": {
            "api_url": {
                "type": "string",
                "format": "uri",
                "pattern": "^https?://",
            },
            "username": {
                "type": "string",
            },
            "password": {
                "type": "string",
            },
            "credential_profile_name": {
                "type": "string",
            },
            "card_technology_id": {
                "type": "integer",
            },
            "cardholder_workgroup_name": {
                "type": "string",
            },
            "client_id": {
                "type": "string",
            },
            "verify_tls": {
                "type": "boolean",
            }
        },
        "required": [
            "api_url", "username", "password", "credential_profile_name",
            "card_technology_id", "cardholder_workgroup_name"
        ],
    }
    DEFAULT_CONFIG = {
        "client_id": "kulkunen",
        "verify_tls": True
    }

    def validate_system_config(self, config):
        jsonschema.validate(self.system.driver_config, self.SYSTEM_CONFIG_SCHEMA)

    def _save_token(self, token):
        self.update_driver_data(dict(token=token.serialize()))

    def _load_token(self):
        data = self.get_driver_data().get('token')
        return SiPassToken.deserialize(data)

    def api_get_token(self):
        username = self.get_setting('username')
        password = self.get_setting('password')

        data = dict(Username=username, Password=password)
        resp = self.api_req_unauth('authentication', 'POST', data=data)
        if not resp['Token']:
            raise Exception("Username or password incorrect")
        token = SiPassToken(value=resp['Token'], expires_at=None)
        self.logger.info("Token: %s" % token.value)
        return token

    def api_renew_session(self):
        self.api_get('authentication')

    @contextmanager
    def ensure_token(self):
        driver_data = self.get_driver_data()
        token_expiration_time = driver_data.get('token_expiration_time')
        token = self._load_token()
        if not token or token.has_expired():
            token = self.api_get_token()

        if not token_expiration_time:
            resp = self.api_req_unauth('authentication/sessiontimeout', 'GET', headers={
                'Authorization': token.value
            })
            if isinstance(resp, int):
                token_expiration_time = resp
            else:
                token_expiration_time = 360  # default
            self.update_driver_data(dict(token_expiration_time=token_expiration_time))

        try:
            yield token
        except Exception as e:
            raise

        token.refresh(token_expiration_time)
        self._save_token(token)

    def api_get(self, path, params=None):
        with self.ensure_token() as token:
            resp = self.api_req_unauth(path, 'GET', params=params, headers={
                'Authorization': token.value
            })
        return resp

    def api_req_unauth(self, path, method, data=None, params=None, headers=None):
        headers = headers.copy() if headers is not None else {}
        headers.update({
            'clientUniqueId': self.get_setting('client_id'),
            'language': 'English'
        })
        verify_tls = self.get_setting('verify_tls')
        url = '%s/%s' % (self.get_setting('api_url'), path)
        self.logger.info('%s: %s' % (method, url))
        if method == 'POST':
            resp = requests.post(url, verify=verify_tls, json=data, headers=headers)
        elif method == 'PUT':
            resp = requests.put(url, verify=verify_tls, json=data, headers=headers)
        elif method == 'GET':
            resp = requests.get(url, verify=verify_tls, params=params, headers=headers)
        else:
            raise Exception("Invalid method")
        if resp.status_code != 200:
            if resp.content:
                try:
                    data = resp.json()
                    err_code = data.get('ErrorCode')
                    err_str = data.get('Message')
                except Exception:
                    err_code = ''
                    err_str = ''
                status_code = resp.status_code
                self.logger.error(f"SiPass API error [HTTP {status_code}] [{err_code}] {err_str}")
            resp.raise_for_status()
        return resp.json()

    def api_post(self, path, data):
        with self.ensure_token() as token:
            resp = self.api_req_unauth(path, 'POST', data, headers={
                'Authorization': token.value
            })
        return resp

    def api_put(self, path, data):
        with self.ensure_token() as token:
            resp = self.api_req_unauth(path, 'PUT', data, headers={
                'Authorization': token.value
            })
        return resp

    def get_cardholders(self):
        params = {
            'searchString': '',
            'appId': 'Cardholders',
            'fields': 'FirstName,LastName,Status',
            'sortingOrder': '{"FieldName":"LastName","Value":"","SortingOrder":0}',
            'filterExpression': "{'Identifier': ''}",
            'startIndex': 0,
            'endIndex': 100,
        }
        resp = self.api_get('Cardholders', params=params)
        return [dict(
            id=d['Token'],
            status=d['Status'],
            first_name=d['FirstName'],
            last_name=d['LastName']
        ) for d in resp['Records']]

import json
import requests
from .modules import requests_toolbelt

class ApiClient:
    def __init__(self, base_url, token=None):
        """
        Initializes a new instance of the ApiClient class.

        Args:
            base_url (str): The base URL of the API.
            token (str, optional): The authentication token to use for requests. Defaults to None.
        """
        self.base_url = base_url
        self.token = token

    def _request(self, method, endpoint, data=None, params=None, custom_headers=None):
        """
        Sends an HTTP request to the API.

        Args:
            method (str): The HTTP method to use for the request.
            endpoint (str): The endpoint to send the request to.
            data (dict, optional): The data to send with the request. Defaults to None.
            params (dict, optional): The query parameters to send with the request. Defaults to None.

        Raises:
            Exception: If the response status code is not in the 200-299 range.

        Returns:
            dict: The JSON response from the server.
        """
        url = self.base_url + endpoint

        if self.token is not None:
          headers = {'Authorization': f"Token {self.token}"}
        else:
          headers = None

        if custom_headers is not None:
            headers = {**headers, **custom_headers} 

        print(headers)
        response = requests.request(method, url, data=data, params=params, headers=headers)

        if response.status_code == 204:
            return {}

        if not response.ok:
            if response.headers.get('content-type') == 'application/json':
                error_data = response.json()
                if 'detail' in error_data:
                    raise Exception(error_data['detail'])
                elif 'non_field_errors' in error_data:
                    raise Exception(error_data['non_field_errors'][0])
                else:
                    raise Exception(error_data)
            else:
                raise Exception(response.text)
        
        return response.json()
    
    def login(self, username:str, password:str):
        """
        Logs in to the API with the specified username and password.

        Args:
            username (str): The username to log in with.
            password (str): The password to log in with.

        Returns:
            dict: The JSON response from the server.
        """
        endpoint = '/auth/token/login'
        data = {'username': username, 'password': password}
        response = self.post(endpoint, data=data)
        self.token = response.get('auth_token')
        return response

    def logout(self):
        """
        Logs out of the API.

        Returns:
            dict: The JSON response from the server.
        """
        endpoint = '/auth/token/logout'
        response = self.post(endpoint)

        self.token = None
        return response

    def get(self, endpoint, params=None):
        """
        Sends a GET request to the specified endpoint.

        Args:
            endpoint (str): The endpoint to send the request to.
            params (dict, optional): The query parameters to send with the request. Defaults to None.

        Returns:
            dict: The JSON response from the server.
        """
        return self._request('GET', endpoint, params=params)

    def post(self, endpoint, data=None, **kwargs):
        """
        Sends a POST request to the specified endpoint.

        Args:
            endpoint (str): The endpoint to send the request to.
            data (dict, optional): The data to send with the request. Defaults to None.

        Returns:
            dict: The JSON response from the server.
        """
        return self._request('POST', endpoint, data=data, **kwargs)

    def put(self, endpoint, data=None, **kwargs):
        """
        Sends a PUT request to the specified endpoint.

        Args:
            endpoint (str): The endpoint to send the request to.
            data (dict, optional): The data to send with the request. Defaults to None.

        Returns:
            dict: The JSON response from the server.
        """
        return self._request('PUT', endpoint, data=data, **kwargs)

    def patch(self, endpoint, data=None, **kwargs):
        """
        Sends a PATCH request to the specified endpoint.

        Args:
            endpoint (str): The endpoint to send the request to.
            data (dict, optional): The data to send with the request. Defaults to None.

        Returns:
            dict: The JSON response from the server.
        """
        m = requests_toolbelt.MultipartEncoder(fields=data)
        return self._request('PATCH', endpoint, data=m, custom_headers={'Content-Type': m.content_type}, **kwargs)

    def delete(self, endpoint):
        """
        Sends a DELETE request to the specified endpoint.

        Args:
            endpoint (str): The endpoint to send the request to.

        Returns:
            dict: The JSON response from the server.
        """
        return self._request('DELETE', endpoint)

    def create_layer(self, fields): 
        '''
        Fields example
            "tag": '[]',
            "title": 'test',
            "description": 'description',
            "data_type": "geojson",
            "options": '{}',
            "file": ('filename', open('poly.geojson', 'rb'), 'application/json')
        '''
        m = requests_toolbelt.MultipartEncoder(fields=fields)

        return self.post('/api/load/user_data/', data=m,
                  custom_headers={'Content-Type': m.content_type})
    

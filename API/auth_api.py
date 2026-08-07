from API.base_api import BaseApi

class AuthApi(BaseApi):
    def login_user(self, payload):
        return self.request.post(
            "/api/login",
            d0ata=payload
        )
    
    def register_user(self, payload):
        return self.request.post(
            "/api/register",
            data=payload,
        )
    
    def refetch_token(self):
        return self.request.get(
            "/api/refetch-token"
        )
    
    def update_user_profile(self, token, payload):
        return self.request.patch(
            "/api/profile",
            headers={
               "Authorization": f"Bearer {token}" 
            },
            data=payload
        )
    
    def logout_profile(self, token):
        return self.request.delete(
            "/api/logout",
            headers={
               "Authorization": f"Bearer {token}" 
            }
        )
    
    def get_profile(self, token):
        return self.request.get(
            "/api/me",
            headers={
               "Authorization": f"Bearer {token}" 
            }    
        )
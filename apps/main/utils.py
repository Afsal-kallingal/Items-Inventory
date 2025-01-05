from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class UserProxy:
    def __init__(self, user_id, fk_organization):
        self.id = user_id  # UUID from the token payload
        self.fk_organization = fk_organization  # Organization ID from the token payload

    def __str__(self):
        return f"UserProxy(id={self.id}, fk_organization={self.fk_organization})"

    @property
    def is_authenticated(self):
        """
        Simulates the behavior of Django's is_authenticated property.
        UserProxy instances represent authenticated users in this context,
        so this always returns True.
        """
        return True


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        # Extract required fields from the JWT token payload
        user_id = validated_token.get("user_id")
        fk_organization = validated_token.get("fk_organization")

        if not user_id or not fk_organization:
            raise AuthenticationFailed("Invalid token payload: missing user_id or fk_organization")

        # Return a proxy user object
        return UserProxy(user_id, fk_organization)

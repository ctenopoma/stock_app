from django.contrib.auth import authenticate
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        print(f"[DEBUG] LoginSerializer.validate - data: {data}")
        user = authenticate(
            username=data.get("username"), password=data.get("password")
        )
        print(f"[DEBUG] LoginSerializer.validate - authenticated user: {user}")
        if not user:
            raise serializers.ValidationError(
                "Unable to log in with provided credentials."
            )
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        data["user"] = user
        return data

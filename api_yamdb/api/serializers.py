from rest_framework import serializers

from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    email = serializers.EmailField()

    class Meta:
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'bio')
        model = User

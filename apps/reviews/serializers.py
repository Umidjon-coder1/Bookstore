from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ('id', 'book', 'user', 'user_name', 'user_avatar', 'rating', 'title', 'body', 'is_approved', 'created_at')
        read_only_fields = ('user', 'is_approved', 'created_at')

    def get_user_avatar(self, obj):
        return obj.user.get_avatar_url()

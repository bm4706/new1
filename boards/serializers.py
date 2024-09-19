from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.nickname', read_only=True)
    image = serializers.ImageField(required=False)

    class Meta:
        model = Post
        fields = ['id', 'author', 'author_name', 'title', 'content', 'image', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at']

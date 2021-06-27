from rest_framework import serializers
from .models import Comment

class PostSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField()
    link = serializers.CharField(required=False)
    score = serializers.IntegerField(read_only=True)
    comment_count = serializers.SerializerMethodField()
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    
    def get_comment_count(self, obj):
        return obj.comment_set.count()

class CommentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    parent_id = serializers.IntegerField(read_only=True)
    text = serializers.CharField()
    score = serializers.IntegerField(read_only=True)
    child_comment_count = serializers.IntegerField(read_only=True)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)

class PostDetailSerializer(PostSerializer):
    comments = serializers.SerializerMethodField()

    def get_comments(self, obj):
        comments = []
        root_comments = []
        source_comments = Comment.objects.filter(post=obj)[:500]
        for comment in source_comments:
            comments.append(CommentSerializer(comment).data)
        for comment in comments:
            target = root_comments
            if comment['parent_id']:
                for parent in comments:
                    if comment['parent_id'] == parent['id']:
                        target = parent.setdefault('child_comments', [])
                        break
            target.append(comment)
        return root_comments
from rest_framework import serializers
from .models import CustomUser,FriendRequest
from .custom_errors import PlainValidationError
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model = CustomUser
        fields=['email','username','password','password2']
        extra_kwargs={
            'password':{'write_only':True}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password != password2:
            raise PlainValidationError({'success': False,'message': 'password and confirm passwprd does not match'})

        return attrs

    def create(self, validate_data):
        return CustomUser.objects.create_user(**validate_data)
    

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=False)
    username = serializers.CharField(max_length=255, required=False)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password']

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        if not email and not username:
            raise serializers.ValidationError('Either email or username must be provided.')

        if not password:
            raise serializers.ValidationError('Password is required.')

        return data
    

class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']



class FriendRequestSerializer(serializers.ModelSerializer):
    receiver_email = serializers.EmailField(write_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'receiver_email', 'status']
        read_only_fields = ['status']

    def validate_receiver_email(self, value):
        try:
            user = CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        request = self.context.get('request')
        if request and user == request.user:
            raise serializers.ValidationError("You cannot send a friend request to yourself.")
        
        return user

    def validate(self, data):
        request = self.context.get('request')
        sender = request.user
        receiver = data.get('receiver_email')

        # Ensure the receiver is not the sender
        if sender.email == receiver:
            raise serializers.ValidationError("You cannot send a friend request to yourself.")
        
        # Check if a friend request already exists
        if FriendRequest.objects.filter(sender=sender, receiver__email=receiver).exists():
            raise serializers.ValidationError("Friend request already sent.")
        
        # Check if users are already friends
        if FriendRequest.objects.filter(
            Q(sender=sender, receiver__email=receiver, status='accepted') |
            Q(sender__email=receiver, receiver=sender, status='accepted')
        ).exists():
            raise serializers.ValidationError("You are already friends with this user.")
        
        # Rate limiting check
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        recent_requests = FriendRequest.objects.filter(sender=sender, created_at__gte=one_minute_ago).count()

        if recent_requests >= 3:
            raise serializers.ValidationError("You have exceeded the limit of 3 friend requests per minute.")
        
        return data

    def create(self, validated_data):
        sender = self.context['request'].user
        receiver = validated_data.pop('receiver_email')
        receiver_user = CustomUser.objects.get(email=receiver)
        
        return FriendRequest.objects.create(sender=sender, receiver=receiver_user)

    

class UserSerializer(serializers.ModelSerializer):

    status = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email','status']


    def get_status(self, obj):
        user = self.context['request'].user
        try:
            friend_request = FriendRequest.objects.get(sender=obj, receiver=user)
            return friend_request.status
        except FriendRequest.DoesNotExist:
            return None 
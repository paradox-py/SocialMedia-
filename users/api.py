from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import( UserRegistrationSerializer,UserLoginSerializer,UserSearchSerializer,UserSerializer)
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from django.db.models import Q
from .models import CustomUser
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from .models import FriendRequest
from .serializers import FriendRequestSerializer
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import APIException


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



class UserRegistrationView(APIView):

    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                token = get_tokens_for_user(user)
                user_data = UserRegistrationSerializer(user).data
                return Response({'user': user_data, 'message': 'User created successfully', 'token': token}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                email = serializer.validated_data.get('email')
                username = serializer.validated_data.get('username')
                password = serializer.validated_data.get('password')

                user = None
                if email:
                    user = authenticate(request, email=email, password=password)
                elif username:
                    user = authenticate(request, username=username, password=password)

                if user is not None:
                    token = get_tokens_for_user(user)
                    return Response({'token': token, 'message': 'Login success'}, status=status.HTTP_200_OK)
                else:
                    return Response({'success': False, 'message': 'Invalid credentials', 'data': None}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UserSearchView(generics.ListAPIView):
    serializer_class = UserSearchSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        username = self.request.query_params.get('username', None)
        email = self.request.query_params.get('email', None)

        if username and email:
            return CustomUser.objects.none()  

        if email:
            # print(CustomUser.objects.filter(email__icontains=email))
            return CustomUser.objects.filter(email__icontains=email)
        elif username:
            return CustomUser.objects.filter(username__icontains=username)
        else:
            return CustomUser.objects.none()  
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)




class SendFriendRequestView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class AcceptRejectFriendRequestView(generics.UpdateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            sender_id = self.request.query_params.get('id')

            if not sender_id:
                raise serializers.ValidationError("Sender ID is required.")

        
            sender = FriendRequest.objects.get(id=sender_id)
            receiver = self.request.user  

            friend_request = FriendRequest.objects.get(sender=sender, receiver=receiver)
            return friend_request

        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Sender does not exist.")
        
        except FriendRequest.DoesNotExist:
            raise serializers.ValidationError("Friend request not found.")
        
        except Exception as e:
            raise serializers.ValidationError(f"An unexpected error occurred: {str(e)}")

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            status_update = request.data.get('status')

            if status_update not in ['accepted', 'rejected']:
                return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

            if instance.status == 'pending':
                instance.status = status_update
                instance.save()

                message = 'Friend request accepted' if status_update == 'accepted' else 'Friend request rejected'
                return Response({'message': message}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'This friend request is no longer pending'}, status=status.HTTP_400_BAD_REQUEST)
        
        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class FriendListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            accepted_requests_as_sender = FriendRequest.objects.filter(sender=user, status='accepted').values_list('receiver', flat=True)
            accepted_requests_as_receiver = FriendRequest.objects.filter(receiver=user, status='accepted').values_list('sender', flat=True)
            
            friend_ids = list(accepted_requests_as_sender) + list(accepted_requests_as_receiver)
            return CustomUser.objects.filter(id__in=friend_ids)
        except FriendRequest.DoesNotExist:
            raise APIException("No friends found.")
        except Exception as e:
            raise APIException(f"An error occurred: {str(e)}")
    

class PendingFriendRequestsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            pending_requests = FriendRequest.objects.filter(receiver=user, status='pending').values_list('sender', flat=True)
            return CustomUser.objects.filter(id__in=pending_requests)

        except FriendRequest.DoesNotExist:
            raise APIException("No pending friend requests found.")
        except Exception as e:
            raise APIException(f"An error occurred: {str(e)}")
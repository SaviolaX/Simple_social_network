from rest_framework.serializers import (ModelSerializer, CharField, ValidationError, SerializerMethodField)

from .models import Profile, FriendRequest

##########################:: Friend requests ::#################################


class FriendRequestSerializer(ModelSerializer):
    """ Serialize all friend requests """
    sender = SerializerMethodField()

    class Meta:
        model = FriendRequest
        fields = ('id', 'sender', 'created_at')

    def get_sender(self, obj):
        profile = Profile.objects.filter(pk=obj.sender.pk).first()
        serializer = ProfileSerializer(profile)
        return serializer.data


class FriendRequestCreateSerializer(ModelSerializer):
    """ Serializer for friend request """

    class Meta:
        model = FriendRequest
        fields = ('id', 'sender', 'receiver', 'created_at')

    def validate(self, data: dict):
        user1: object = data['sender']
        user2: object = data['receiver']

        # check wether sender sent a request before
        req_from_user1 = FriendRequest.objects.filter(sender=user1,
                                                      receiver=user2).first()
        if req_from_user1 != None:
            raise ValidationError({'message': 'Request has sent already'})

        # check wether receiver sent a request to sender before
        req_from_user2 = FriendRequest.objects.filter(sender=user2,
                                                      receiver=user1).first()
        if req_from_user2 != None:
            raise ValidationError(
                {'message': 'The user has sent request to you already'})

        if user1 in user2.friends.all():
            raise ValidationError(
                {'message': 'This user is in your friend list already.'})

        return data


#######################:: Profile detail/update ::##############################


class ProfileSerializer(ModelSerializer):
    """ Serializer for Profile """

    class Meta:
        model = Profile
        fields = ('id', 'email', 'username', 'image')


class ProfileDetailSerializer(ModelSerializer):
    """ Serializer for Profile """
    friend_requests = SerializerMethodField()
    friends = SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('id', 'email', 'username', 'image', 'friends',
                  'friend_requests')

    def get_friends(self, obj):
        friend_list = Profile.objects.filter(pk=obj.pk).first().friends
        serializer = ProfileSerializer(friend_list, many=True)
        return serializer.data

    def get_friend_requests(self, obj):
        """ Get a list of all requests sent to current user """
        reqs = FriendRequest.objects.filter(receiver=obj.id)
        serializer = FriendRequestSerializer(reqs, many=True)
        return serializer.data


###########################:: Authentication ::#################################


class LoginProfileSerializer(ModelSerializer):
    """ Serializer for Profile login """
    email = CharField(max_length=255, required=True)
    password = CharField(max_length=255, write_only=True, required=True)

    class Meta:
        model = Profile
        fields = ('id', 'email', 'password')


class RegisterProfileSerializer(ModelSerializer):
    """ Serializer for Profile registration """
    email = CharField(max_length=255, required=True)
    password = CharField(max_length=255, write_only=True, required=True)
    confirm_password = CharField(max_length=255,
                                 write_only=True,
                                 required=True)

    class Meta:
        model = Profile
        fields = ('id', 'email', 'password', 'confirm_password')

    def validate(self, data):
        """ Validate all data from request """
        # check for empty fields
        if data['email'] == '':
            raise ValidationError({'error': 'Email is required'})
        if data['password'] == '':
            raise ValidationError({'error': 'Password is required'})
        if data['confirm_password'] == '':
            raise ValidationError({'error': 'Confirm password is required'})

        # validate email
        splited_email = [x for x in data['email']]
        if '@' not in splited_email:
            raise ValidationError({'error': 'Invalid email format'})

        # check for password min length
        if len(data['password']) < 6:
            raise ValidationError(
                {'error': 'Password is too short. It has to be min 6 char'})

        # check password match
        if data['password'] != data['confirm_password']:
            raise ValidationError({'error': 'Passwords do not match'})

        user = Profile.objects.filter(email=data['email']).first()
        username = data['email'].strip().rsplit('@', 1)[0]

        if user is not None:
            raise ValidationError(
                {'error': 'User with this email already exists'})

        validated_data = dict(email=data['email'],
                              username=username,
                              password=data['password'])
        return validated_data

    def create(self, validated_data):
        """ Default 'create' view changed for hashing password """
        new_user = Profile.objects.create_user(**validated_data)
        return new_user

from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from connected_group_project import settings

MAX_LENGTH_NAME = 128

class Category(models.Model):
    name = models.CharField(max_length=MAX_LENGTH_NAME, unique=True)
    slug = models.SlugField(unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name
    
class Event(models.Model):
    TITLE_MAX_LENGTH = 128
    URL_MAX_LENGTH = 200
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=TITLE_MAX_LENGTH)
    date = models.CharField(max_length=10)
    url = models.URLField()
    signups = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    friends = models.ManyToManyField('self', symmetrical=True, related_name='friends_plus', blank=True)
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username
    
class Tab(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    monday_schedule = models.TextField(blank=True, null=True)
    tuesday_schedule = models.TextField(blank=True, null=True)
    wednesday_schedule = models.TextField(blank=True, null=True)
    thursday_schedule = models.TextField(blank=True, null=True)
    friday_schedule = models.TextField(blank=True, null=True)
    saturday_schedule = models.TextField(blank=True, null=True)
    sunday_schedule = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Friend(models.Model):
    users = models.ManyToManyField(User, related_name='friends')
    created = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=False, editable=True)

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friend_requests_received', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
class Friendship(models.Model):
    from_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="friendship_creator_set")
    to_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="friend_set")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user} friends with {self.to_user}"

    class Meta:
        unique_together = ('from_user', 'to_user')

class ScheduleEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day = models.CharField(max_length=9)  # E.g., "Monday"
    start_time = models.TimeField()
    end_time = models.TimeField()
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    # Additional fields as necessary...
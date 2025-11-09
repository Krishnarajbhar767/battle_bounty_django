from django.db import models

from django.conf import settings
class Tournament(models.Model) :
    STATUS_CHOICES = [('completed', 'Completed'), ('ongoing', 'Ongoing'), ('upcoming', 'Upcoming')]
    TEAM_CHOICES = [('solo', 'Solo'), ('duo', 'Duo'), ('squad', 'Squad'), ('custom', 'Custom')]
    game = models.CharField(max_length=100)
    mode = models.CharField(max_length=100)
    map_name = models.CharField(max_length=100)
    team_type = models.CharField(max_length=10, choices=TEAM_CHOICES)
    max_players = models.PositiveIntegerField()
    max_team_size = models.PositiveIntegerField()
    start_at = models.DateTimeField()
    room_id = models.CharField(max_length=100)
    room_password = models.CharField(max_length=100)
    thumbnail = models.URLField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.game} - {self.mode}"


class GameProfile(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('verified', 'Verified'), ('rejected', 'Rejected')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='game_profiles')
    game = models.CharField(max_length=100)
    in_game_name = models.CharField(max_length=100)
    in_game_id = models.CharField(max_length=100)
    screenshot_proof = models.URLField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(blank=True)


class Team(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='teams')
    captain = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='captain_teams')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='member_teams', blank=True)

    def __str__(self):
        return f"{self.tournament.game} | Captain: {self.captain.username}"
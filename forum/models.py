from django.urls import reverse
from django.db import models

from base.models import BaseComment
from members.models import Member
from polls.models import Poll


class Post(models.Model):
    """
    Store a forum post.

    A post can have an optional :model:`polls.Poll`.

    last_activity timestamp is updated when the post
    is changed, or a comment is posted.

    Access to the board forum is restricted by permission.
    """
    # The names in the constants are used in the database and urls,
    # while the alternatives in FORUM_CHOICES are displayed on the page
    MUSIC = 'musikk'
    VARIOUS = 'diverse'
    BOARD = 'styret'
    FORUM_CHOICES = (
        (MUSIC, 'Musikk og noter'),
        (VARIOUS, 'Diverse'),
        (BOARD, 'Styret'),
    )

    title = models.CharField('tittel', max_length=255)
    content = models.TextField('innlegg')
    forum = models.CharField('forum', max_length=10,
                             choices=FORUM_CHOICES, default=VARIOUS)
    poster = models.ForeignKey(Member, null=True, on_delete=models.SET_NULL)
    poll = models.OneToOneField(Poll, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'forumpost'
        verbose_name_plural = 'forumposter'
        ordering = ('-last_activity', '-created')
        permissions = (
            ('view_board_forum', 'Kan se styreforumet'),
        )

    def __str__(self):
        """Return the title of the post."""
        return self.title

    def get_absolute_url(self):
        return reverse('forum_post_detail', kwargs={'pk': self.pk, 'forum': self.forum})

    @classmethod
    def user_can_access_forum(cls, user, forum):
        """Return whether or not the user can access the forum."""
        return forum != cls.BOARD or user.has_perm('forum.view_board_forum')

    @classmethod
    def available_forums(cls, user):
        """
        Returns a tuple, formated like FORUM_CHOICES above,
        with the forums the given user has access to.
        """
        result = tuple()
        for forum in cls.FORUM_CHOICES:
            if not cls.user_can_access_forum(user, forum[0]):
                continue
            result += (forum,)

        return result


class ForumComment(BaseComment):
    """Store a comment for a :model:`forum.Post`."""
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        """
        Save the comment to the database, and update
        the last_activity timestamp on the related
        :model:`forum.Post`.
        """
        super(ForumComment, self).save(*args, **kwargs)
        post = self.post
        post.last_activity = self.created
        post.save()

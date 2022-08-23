from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from hitcount.models import HitCount
from django.contrib.contenttypes.fields import GenericRelation

# Create your models here.
from django.conf import settings
from django.utils.text import slugify
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
import os
from PIL import Image


def upload_location(instance, filename):
    file_path = 'blogPost/user_{author_id}/{slug}_post.jpeg'.format(
        author_id=str(instance.author.id), slug=str(instance.slug), filename=filename
    )
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    if os.path.exists(full_path):
        os.remove(full_path)
    return file_path


class Category(models.Model):
    category_name = models.CharField(max_length=50, null=True, default='others', blank=False)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.category_name


class BlogPost(models.Model):
    title = models.CharField(max_length=50, null=False, blank=False)
    category = models.ManyToManyField(Category, verbose_name='categories')
    body = RichTextUploadingField(null=False, blank=False)
    image = models.ImageField(upload_to=upload_location, null=False, blank=False)
    date_published = models.DateTimeField(auto_now_add=True, verbose_name="date published")
    date_updated = models.DateTimeField(auto_now=True, verbose_name="date updated")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="author")
    slug = models.SlugField(blank=True, unique=True)
    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk',
                                        related_query_name='hit_count_generic_relation')

    def get_absolute_url(self):
        return reverse('blogPost:details', args=[self.slug])

    class Meta:
        ordering = (
            '-date_published',
        )

    def __str__(self):
        return self.title


@receiver(post_delete, sender=BlogPost)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)


@receiver(post_save, sender=BlogPost)
def save_img(sender, instance, *args, **kwargs):
    if instance.image:
        SIZE = 600, 600
        pic = Image.open(instance.image.path)
        if pic.mode in ("RGBA", 'P'):
            pic = pic.convert("RGB")
            pic.thumbnail(SIZE, Image.LANCZOS)
            pic.save(instance.image.path)


def pre_save_blog_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.author.username + "-" + instance.title)


pre_save.connect(pre_save_blog_post_receiver, sender=BlogPost)


# comment
class Comment(MPTTModel):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="comments")
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="comment_parent")
    name_comment = models.CharField(max_length=50)
    email_comment = models.EmailField(null=True)
    username_comment = models.CharField(max_length=50, null=True)
    content = models.TextField()
    date_published = models.DateTimeField(auto_now_add=True)

    class MPTTMeta:
        order_insertion_by = ("-date_published",)

    def __str__(self):
        return f"Comment by {self.name_comment}"


# likes
LIKE_CHOICES = (
    ('Like', 'Like'),
    ('Unlike', 'Unlike')
)


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE,
                             related_name='user_like')
    postLike = models.ForeignKey(BlogPost, on_delete=models.CASCADE, null=True, related_name='like_post_value')
    value = models.CharField(choices=LIKE_CHOICES, default='Like', max_length=10,
                             null=True, blank=True)

    def __str__(self):
        obj_user = str(self.user)
        obj_post = str(self.postLike)
        obj_value = str(self.value)
        return f"{obj_user}_({obj_value})_{obj_post}"

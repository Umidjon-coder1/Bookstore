from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.books.models import Book


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('book', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.book.title} ({self.rating}/5)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_book_rating()

    def delete(self, *args, **kwargs):
        book = self.book
        super().delete(*args, **kwargs)
        self._update_book_rating(book)

    def _update_book_rating(self, book=None):
        book = book or self.book
        reviews = Review.objects.filter(book=book, is_approved=True)
        count = reviews.count()
        avg = reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0
        Book.objects.filter(pk=book.pk).update(rating=round(avg, 2), reviews_count=count)

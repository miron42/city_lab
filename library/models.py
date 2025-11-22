from django.db import models


class Author(models.Model):
    full_name = models.CharField(max_length=255)
    birth_date = models.DateField()

    def __str__(self):
        return self.full_name


class Book(models.Model):
    title = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} ({self.year})"


class Library(models.Model):
    name = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class LibraryBook(models.Model):
    """
    Каждая книга находится ровно в одной библиотеке.
    """

    library = models.ForeignKey(Library, related_name="books", on_delete=models.CASCADE)
    book = models.OneToOneField(
        Book, related_name="placement", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("library", "book")

    def __str__(self):
        return f"{self.book} @ {self.library}"

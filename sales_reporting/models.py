from django.db import models


class Store(models.Model):
    number = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.number} - {self.name}"


class Category(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.PROTECT,
    )

    level = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255)

    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.PROTECT,
    )

    class Meta:
        ordering = ["description"]

    def __str__(self):
        return f"{self.sku} - {self.description}"


class SalesImport(models.Model):
    source_filename = models.CharField(max_length=255)

    store = models.ForeignKey(
        Store,
        related_name="imports",
        on_delete=models.PROTECT,
    )

    from_date = models.DateField()
    to_date = models.DateField()
    reporting_month = models.DateField()
    channel = models.CharField(max_length=50, blank=True)

    imported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-from_date", "store"]

    def __str__(self):
        return f"{self.store.number} - {self.from_date:%B %Y}"


class SalesRecord(models.Model):
    sales_import = models.ForeignKey(
        SalesImport,
        related_name="sales_records",
        on_delete=models.CASCADE,
    )

    product = models.ForeignKey(
        Product,
        related_name="sales_records",
        on_delete=models.PROTECT,
    )

    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    sales = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    cogs = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    gross_margin = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    margin_percentage = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=0,
    )

    class Meta:
        ordering = ["product__description"]

class CategoryResult(models.Model):
    sales_import = models.ForeignKey(
        SalesImport,
        related_name="category_results",
        on_delete=models.CASCADE,
    )

    category = models.ForeignKey(
        Category,
        related_name="results",
        on_delete=models.PROTECT,
    )

    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    sales = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    cogs = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    gross_margin = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    margin_percentage = models.DecimalField(
        max_digits=8,
        decimal_places=6,
        default=0,
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("sales_import", "category"),
                name="unique_category_result_per_import",
            ),
        )

    def __str__(self):
        return (
            f"{self.sales_import} - "
            f"{self.category.code}"
        )
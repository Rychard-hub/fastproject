from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class BlogPost(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    author = fields.CharField(max_length=100)
    file_path = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    published = fields.BooleanField(default=False)

    class Meta:
        table = "blog_posts"

    def __str__(self):
        return self.title

class Product(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField()
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    image_url = fields.CharField(max_length=255, null=True)
    stripe_price_id = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "products"

    def __str__(self):
        return self.name

class ProTip(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    content = fields.TextField()

    class Meta:
        table = "pro_tips"

    def __str__(self):
        return self.title

class Benefit(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField()

    class Meta:
        table = "benefits"

    def __str__(self):
        return self.title

class Routine(models.Model):
    id = fields.IntField(pk=True)
    icon = fields.CharField(max_length=10)
    level = fields.CharField(max_length=50)
    title = fields.CharField(max_length=255)
    target = fields.CharField(max_length=100)
    steps = fields.JSONField()
    timing = fields.CharField(max_length=100)

    class Meta:
        table = "routines"

    def __str__(self):
        return self.title

BlogPost_Pydantic = pydantic_model_creator(BlogPost, name="BlogPost")
BlogPostIn_Pydantic = pydantic_model_creator(BlogPost, name="BlogPostIn", exclude_readonly=True)
Product_Pydantic = pydantic_model_creator(Product, name="Product")
ProductIn_Pydantic = pydantic_model_creator(Product, name="ProductIn", exclude_readonly=True)
Benefit_Pydantic = pydantic_model_creator(Benefit, name="Benefit")
Routine_Pydantic = pydantic_model_creator(Routine, name="Routine")
ProTip_Pydantic = pydantic_model_creator(ProTip, name="ProTip")

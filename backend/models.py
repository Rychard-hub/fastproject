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

BlogPost_Pydantic = pydantic_model_creator(BlogPost, name="BlogPost")
BlogPostIn_Pydantic = pydantic_model_creator(BlogPost, name="BlogPostIn", exclude_readonly=True)
Product_Pydantic = pydantic_model_creator(Product, name="Product")
ProductIn_Pydantic = pydantic_model_creator(Product, name="ProductIn", exclude_readonly=True)

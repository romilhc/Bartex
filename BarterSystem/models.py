from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
'''
# Create your models here.
class User(models.Model):
    fname = models.CharField(max_length=40,null=False)
    lname = models.CharField(max_length=40,null=False)
    uid = models.AutoField(max_length=40,primary_key=True,null=False)
    email = models.EmailField(max_length=100,unique=True,null=False)
    age = models.PositiveIntegerField(null=False)

    Male = 'M'
    Female = 'F'
    Gender = ((Male, 'M'), (Female, 'F'))
    gender = models.CharField(max_length=1,choices=Gender,default=Male,null=False)

    street = models.CharField(max_length=150,null=False)
    city = models.CharField(max_length=40,null=False)
    state = models.CharField(max_length=40,null=False)
    country = models.CharField(max_length=40,null=False)
    zipcode = models.CharField(max_length=10,null=False)
    contact = models.CharField(max_length=15,null=False)
    profession = models.CharField(max_length=20,null=True)
    password = models.CharField(max_length=20,null=False)

class ProductCategory(models.Model):
    cid = models.AutoField(primary_key=True,null=False)
    cname = models.CharField(max_length=40,null=False)


class Post(models.Model):
    pid = models.AutoField(primary_key=True,null=False)
    uid = models.ForeignKey('User',on_delete=models.CASCADE,null=False)
    product_name = models.CharField(max_length=40,null=False)
    product_desc = models.CharField(max_length=150,null=False)
    product_age = models.PositiveIntegerField(null=False)
    cid = models.ForeignKey('ProductCategory',on_delete=models.CASCADE,null=False)

    Active = 'A'
    Passive = 'P'
    Post_Status = ((Active, 'A'), (Passive, 'P'))
    post_status = models.CharField(max_length=1,choices=Post_Status,default=Active,null=False)
    post_timestamp = models.DateTimeField(auto_now=True, primary_key=True, null=False)
    estimated_price = models.DecimalField(max_digits=15,decimal_places=3,default=0.0)

class SwapChoice(models.Model):
    pid = models.ForeignKey('Post',on_delete=models.CASCADE,primary_key=True,null=False)
    cid = models.ForeignKey('ProductCategory',on_delete=models.CASCADE,primary_key=True,null=False)

class Tag(models.Model):
    pid = models.ForeignKey('Post',on_delete=models.CASCADE,primary_key=True,null=False)
    tag_name = models.CharField(primary_key=True,null=False,max_length=40)

class Swap(models.Model):
    senderPid = models.ForeignKey('Post',on_delete=models.CASCADE,primary_key=True)
    receiverPid= models.ForeignKey('Post',on_delete=models.CASCADE,primary_key=True)

    Accepted = 'A'
    Rejected = 'R'
    Pending = 'P'
    Swap_Status = ((Accepted, 'A'), (Rejected, 'R'), (Pending, 'P'))
    swap_status = models.CharField(max_length=1, choices=Swap_Status, default=Pending, null=False)
    swap_timestamp = models.DateTimeField(auto_now=True, primary_key=True, null=False)


class PostReviews(models.Model):
    uid = models.ForeignKey('User', on_delete=models.CASCADE,primary_key=True,null=False)
    pid = models.ForeignKey('Post',on_delete=models.CASCADE,primary_key=True, null=False)
    comment = models.CharField(max_length=150,null=False)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(0),MaxValueValidator(5)])
    post_review_timestamp = models.DateTimeField(auto_now=True, primary_key=True, null=False)

class UserReviews(models.Model):
    commentingUid = models.ForeignKey('User', on_delete=models.CASCADE,primary_key=True,null=False)
    commentOnUid = models.ForeignKey('User',on_delete=models.CASCADE,primary_key=True, null=False)
    comment = models.CharField(max_length=150,null=False)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(0),MaxValueValidator(5)])
    user_review_timestamp = models.DateTimeField(auto_now=True, primary_key=True, null=False)



class Like(models.Model):
    uid =  models.ForeignKey('User', on_delete=models.CASCADE, primary_key=True, null=False)
    pid = models.ForeignKey('Post', on_delete=models.CASCADE, primary_key=True, null=False)
    like_timestamp = models.DateTimeField(auto_now=True, primary_key=True, null=False)

class Favourite(models.Model):
    uid = models.ForeignKey('User', on_delete=models.CASCADE, primary_key=True, null=False)
    pid = models.ForeignKey('Post', on_delete=models.CASCADE, primary_key=True, null=False)
    favourite_timestamp = models.DateTimeField(auto_now=True, primary_key=True, null=False)
'''












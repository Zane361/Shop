from django.db import models
from django.contrib.auth.models import AbstractUser
from random import sample
from datetime import datetime
import string
import qrcode
from PIL import Image
from io import BytesIO

class CodeGenerate(models.Model):
    code = models.CharField(max_length=255, blank=True,unique=True)
    
    @staticmethod
    def generate_code():
        return ''.join(sample(string.ascii_letters + string.digits, 15)) 
    
    def save(self, *args, **kwargs):
        if not self.id:
            while True:
                code = self.generate_code()
                if not self.__class__.objects.filter(code=code).count():
                    self.code = code
                    break
        super(CodeGenerate,self).save(*args, **kwargs)

    class Meta:
        abstract = True


class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatar/',default='avatar/default.png')
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.IntegerField(blank=True, null=True)
    
    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"
    
    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = 'default.png'
        super().save(*args, **kwargs)
    

class Category(CodeGenerate):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Product(CodeGenerate):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    body = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    discount_price = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    banner_img = models.ImageField(upload_to='banner-img/')
    quantity = models.IntegerField() 
    delivery = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    qrcode_img = models.ImageField(blank=True, upload_to='qrcode-img/')

    def __str__(self):
        return self.name

    @property 
    def stock_status(self):
        return bool(self.quantity)
    
    def save(self, *args, **kwargs):
        qr_image = qrcode.make(self.name, box_size=15)
        qr_image_pil = qr_image.get_image()
        stream = BytesIO()
        qr_image_pil.save(stream, format='PNG')
        self.qrcode_img.save(f"{self.name}.png", BytesIO(stream.getvalue()), save=False)
        super(Product, self).save(*args, **kwargs)
    

class EnterProduct(CodeGenerate):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name
    
    def save(self, *args, **kwargs):
        if self.pk:
            object = EnterProduct.objects.get(id=self.id)
            self.product.quantity -= object.quantity
        self.product.quantity +=self.quantity
        self.product.save()
        super(EnterProduct, self).save(*args, **kwargs)


class ProductImg(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    img = models.ImageField(upload_to='img/')


class ProductVideo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    video = models.FileField(upload_to='video', blank=True, null=True)
    link = models.URLField(null=True, blank=True)


class Review(models.Model):
    mark = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()

    @property
    def mark_iter(self):
        return range(self.mark)

    def save(self, *args, **kwargs):
        if not self.mark in (1, 2, 3, 4, 5):
            print(self.mark)
            raise ValueError("1 dan 5 gacha bo'lgan baho bering!")
        if self.pk:
            obj = Review.objects.filter(product=self.product, user=self.user).exclude(pk=self.pk).first()
        else:
            obj = Review.objects.filter(product=self.product, user=self.user).first()
        
        if obj:
            obj.mark = self.mark
            obj.text = self.text
        super(Review, self).save(*args, **kwargs)


class Cart(CodeGenerate):
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    status = models.IntegerField(
        choices=(
            (1, 'No  faol'),
            (2, "Yo'lda"),
            (3, 'Qaytarilgan'),
            (4, 'Qabul qilingan'),  
        )
    )
    order_date = models.DateTimeField(null=True, blank=True)

    @property
    def total(self):
        count = 0
        queryset = CartProduct.objects.filter(cart = self)
        for i in queryset:
            count += i.count
        return count
    
    @property
    def price(self):
        count = 0
        queryset = CartProduct.objects.filter(cart = self)
        for i in queryset:
            if i.product.discount_price:
                count += i.count * i.product.discount_price
            else:
                count += i.count * i.product.price
        return count
    
    @property
    def total_price(self):
        count = 0
        queryset = CartProduct.objects.filter(cart = self)
        for i in queryset:
            count += i.count * i.product.price
        return count
 
    def save(self, *args, **kwargs):
        if self.status == 2 and Cart.objects.get(id=self.id).status == 1 :
            self.order_date = datetime.now()
        super(Cart, self).save(*args, **kwargs )


class CartProduct(models.Model):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    count = models.IntegerField()

    @property
    def price(self):
        return self.count * self.product.price
    
    @property
    def discount_price(self):
        try:
            return self.count * self.product.discount_price
        except:
            return None
    
    @property
    def date(self):
        return self.cart.order_date
    

class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if WishList.objects.filter(user=self.user, product=self.product).count():
            raise ValueError('Dual')
        super(WishList, self).save(*args, **kwargs)

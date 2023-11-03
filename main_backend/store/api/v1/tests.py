from urllib.request import urlopen
from urllib.parse import urlparse
from io import BytesIO
from django.core.files.images import ImageFile
import requests
from store.models import Product, Album, Category
from django.contrib.contenttypes.models import ContentType

user_id = 1

response = requests.get("https://dummyjson.com/products?limit=100").json()
for every_prod in response["products"]:
  try:
    cate = Category.objects.get(name=every_prod["category"])
  except Exception as e:
    print(e)
    cate = Category.objects.create(name=every_prod["category"], created_by_id=user_id)
  finally:
    cate = Category.objects.get(name=every_prod["category"])
    sing_pd = Product.objects.create(category=cate, created_by_id=user_id, title=every_prod["title"], description=every_prod["description"], price=every_prod["price"])
    url = every_prod["thumbnail"]
    image_file_name = urlparse(url).path.split('/')[-1]
    image_file_content = BytesIO(urlopen(url).read())
    sing_pd.thumbnail.save(image_file_name, image_file_content)
    for image in every_prod["images"]:
      al = Album.objects.create(created_by_id=user_id, content_type=ContentType.objects.get(model="product", app_label="store"), object_id=sing_pd.pk)
      image_file_name = urlparse(image).path.split('/')[-1]
      image_file_content = BytesIO(urlopen(image).read())
      al.image.save(image_file_name, image_file_content)
      
# Django-Gallery

基于[Django](https://github.com/django/django)和[Blueimp Gallery](https://github.com/blueimp/Gallery)的照片墙应用程序。

运行截图：
![1](demo/1.png)
![2](demo/2.png)


## 使用方法
1. Clone this repo
```
git clone https://github.com/lijg/Image-Gallery.git
```

2. virtualenv
```
virtualenv django
source django/bin/activate
pip install -r Image-Gallery/requirements.txt
```

3. run
```
cd Image-Gallery
python manage.py makemigrations gallery
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

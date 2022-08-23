import urllib.request
import os


def testingImage(image_url, filename):
    image_url = image_url

    filename = filename

    req = urllib.request.build_opener()
    req.addheaders = [('user-agent', 'Mozilla/5.0 (Windows NT 6.1; WDW64)')]
    urllib.request.install_opener(req)

    urllib.request.urlretrieve(image_url, filename)


def create_or_get_path(path):
    path = path
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        print("success")

    else:
        print("path exit")

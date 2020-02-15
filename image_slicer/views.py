import os
import urllib.parse
import urllib.request
import uuid

from PIL import Image as PILImage
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from google.cloud import storage

from slicedog.settings import GCP_BUCKET
from .image_slicer import slice_image_iterations
from .models import Image

storage_client = storage.Client()

def index_view(request):

    error_message = ""

    if request.method == 'POST':
        if not request.FILES.get('uploaded-file', False):
            error_message = 'No file selected'
        else:
            uploaded_image = request.FILES['uploaded-file']
            if uploaded_image.size > 5242880:
                error_message = 'Files must be smaller than 5mb'
            else:
                try:
                    image = PILImage.open(uploaded_image)
                    image.verify()
                    uploaded_image.seek(0)

                    filepath = 'image_slicer/' + str(uuid.uuid4())
                    bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
                    blob = bucket.blob(filepath)
                    blob.upload_from_file(uploaded_image)

                    db_image = Image(
                        path=filepath,
                        width=image.width,
                        height=image.height
                    )
                    db_image.save()
                except Exception as error:
                    print(error)
                    error_message = 'Could not import file as an image'

    images = Image.objects.all()
    return render(request, 'image_slicer/index.html', {
        'images': images,
        'bucket_root': GCP_BUCKET,
        'error_message': error_message
    })


# just serving the dynamically generated image
def sliced_view(request, image_id):
    image_entry = get_object_or_404(Image, pk=image_id)

    # image_url = request.scheme + '://' + request.get_host() + static(image_entry.path) # used locally
    image_url = GCP_BUCKET + image_entry.path

    image = PILImage.open(urllib.request.urlopen(image_url))
    response = HttpResponse(content_type="image/jpeg")

    vertical_strips = request.GET.get('v') or 1
    horizontal_strips = request.GET.get('h') or 1
    iterations = request.GET.get('i') or 1

    try:
        image = slice_image_iterations(
            image,
            vstrips=int(vertical_strips),
            hstrips=int(horizontal_strips),
            iterations=int(iterations))
    except ValueError as error:
        return HttpResponseBadRequest(error)

    image = image.convert('RGB')
    image.save(response, 'JPEG')
    return response


def detail_view(request, image_id):
    image_entry = get_object_or_404(Image, pk=image_id)
    return render(request, 'image_slicer/detail.html', {
        'image': image_entry,
        'sliced_url': url_with_querystring(
            reverse('image_slicer:sliced', args=[image_id]),
            request.GET),
        'bucket_root': GCP_BUCKET

    })


def url_with_querystring(path, parameters):
    parameters = {k: v for (k, v) in parameters.items() if v is not None}
    if parameters:
        return path + '?' + urllib.parse.urlencode(parameters)
    return path






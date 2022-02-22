import os
import requests
import pandas as pd

from django.utils import timezone
from django.db import transaction
from celery import shared_task

from products.models import Product, ProcessedFileHistory
from webhooks.models import WebHook


def to_product_object(data): return Product(
    name=data["name"],
    sku=data["sku"],
    description=data["description"]
)


def _update_product(product, data):
    product.name = data["name"]
    product.description = data["description"]
    product.updated_at = timezone.now()

    return product


def _bulk_update_products(skus, chunk):
    chunk_to_update = chunk.loc[chunk["sku"].isin(skus)].copy()
    products_to_update = Product.objects.filter(sku__in=skus)
    objects_to_update = list()
    for product in products_to_update.iterator():
        data = chunk_to_update.loc[chunk["sku"] == product.sku].iloc[0]
        objects_to_update.append(_update_product(product, data))

    Product.objects.bulk_update(
        objects_to_update, ["name", "description", "updated_at"])


def _bulk_insert_products(skus, chunk):
    chunk_to_insert = chunk.loc[chunk["sku"].isin(skus)]
    chunk_to_insert = chunk_to_insert.to_dict("records")
    objects_to_insert = list(map(to_product_object, chunk_to_insert))
    Product.objects.bulk_create(objects_to_insert, ignore_conflicts=True)


@shared_task
def ingest_products_data(file_url, file_sha256):

    # check file already processed using SHA256 or not.
    is_file_history_exists = ProcessedFileHistory.objects.filter(
        sha256=file_sha256).count() > 0

    if not is_file_history_exists:
        # New Imported file, process the insertion/updation
        # process 1000s records at once
        for chunk in pd.read_csv(file_url, chunksize=1000):
            skus = set(chunk["sku"].to_list())
            # check the existing skus of file from database table
            existing_skus = Product.objects.filter(
                sku__in=skus).values_list('sku', flat=True)
            existing_skus = set(existing_skus)

            # Get the skus which are not present in database table
            non_existing_skus = skus - existing_skus

            # Bulk Update
            if existing_skus:
                _bulk_update_products(existing_skus, chunk)

            # Bulk insert
            if non_existing_skus:
                _bulk_insert_products(non_existing_skus, chunk)

        # Save history for new file
        ProcessedFileHistory.objects.create(sha256=file_sha256)

    # Remove the file from media storage after processing
    os.remove(file_url)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=20, retry_kwargs={'max_retries': 2})
@transaction.atomic
def ingest_products_data_v2(self, data):
    df = pd.DataFrame(data)
    skus = set(df["sku"].to_list())
    # check the existing skus of file from database table
    existing_skus = Product.objects.filter(
        sku__in=skus).values_list('sku', flat=True)
    existing_skus = set(existing_skus)

    # Get the skus which are not present in database table
    non_existing_skus = skus - existing_skus

    # Bulk Update
    if existing_skus:
        _bulk_update_products(existing_skus, df)

    # Bulk insert
    if non_existing_skus:
        _bulk_insert_products(non_existing_skus, df)


def _send_webhook_request(url, params):
    try:
        response = requests.get(url, params=params)
        assert response.status_code == 200
    except AssertionError:
        print(f"WebHook Request to {url} Failed")


@shared_task
def notify_webhooks(product_id):
    try:
        product = Product.objects.get(id=product_id)
        webhooks_qs = WebHook.objects.filter(active=True)
        # notify webhooks
        for whook in webhooks_qs.iterator():
            # Product details as query param
            params = {
                'product_id': product_id,
                'name': product.name,
                'sku': product.sku
            }
            _send_webhook_request(whook.url, params)
    except Product.DoesNotExist:
        print("Invalid product_id provided")

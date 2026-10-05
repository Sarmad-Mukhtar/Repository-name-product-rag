import os

import psycopg
from elasticsearch import Elasticsearch, helpers


DATABASE_URL = os.environ["PRODUCT_RAG_DATABASE_URL"]

ELASTICSEARCH_URL = "http://localhost:9201"


INDEX_NAME = "products_vendor_improve_rag"


def main():
    es = Elasticsearch(ELASTICSEARCH_URL)

    if not es.ping():
        raise RuntimeError("Could not connect to Elasticsearch")

    print("Connected to Elasticsearch")

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    description,
                    manufacturer_id,
                    manufacturer_name,
                    category_id,
                    category,
                    axe_part_no,
                    mfg_part_no,
                    upc,
                    list_price,
                    regular_cost,
                    quantity,
                    stock_status,
                    pricing_status,
                    status,
                    product_type,
                    is_active,
                    is_bundle,
                    is_similar,
                    is_valid_for_excel_processing,
                    manufacturer_corrected,
                    energy_star,
                    section_508,
                    end_user_info,
                    weight,
                    height,
                    width,
                    length,
                    specification,
                    searchable_text,
                    created_on,
                    updated_on,
                    category_path,
                    attribute_tags,
                    images,
                    vendor_info,
                    specifications,
                    manufacturer_names_seen,
                    validation_flags,
                    data_quality_flag,
                    raw_data
                FROM products
                """
            )

            rows = cursor.fetchall()

    print(f"Products loaded from PostgreSQL: {len(rows)}")

    columns = [
        "id",
        "name",
        "description",
        "manufacturer_id",
        "manufacturer_name",
        "category_id",
        "category",
        "axe_part_no",
        "mfg_part_no",
        "upc",
        "list_price",
        "regular_cost",
        "quantity",
        "stock_status",
        "pricing_status",
        "status",
        "product_type",
        "is_active",
        "is_bundle",
        "is_similar",
        "is_valid_for_excel_processing",
        "manufacturer_corrected",
        "energy_star",
        "section_508",
        "end_user_info",
        "weight",
        "height",
        "width",
        "length",
        "specification",
        "searchable_text",
        "created_on",
        "updated_on",
        "category_path",
        "attribute_tags",
        "images",
        "vendor_info",
        "specifications",
        "manufacturer_names_seen",
        "validation_flags",
        "data_quality_flag",
        "raw_data",
    ]

    actions = []

    for row in rows:
        product = dict(zip(columns, row))

        document = {
            "Id": product["id"],
            "Name": product["name"],
            "Description": product["description"],
            "ManufacturerId": product["manufacturer_id"],
            "ManufacturerName": product["manufacturer_name"],
            "CategoryId": product["category_id"],
            "Category": product["category"],
            "AXEPartNo": product["axe_part_no"],
            "MFGPartNo": product["mfg_part_no"],
            "UPC": product["upc"],
            "ListPrice": product["list_price"],
            "RegularCost": product["regular_cost"],
            "Quantity": product["quantity"],
            "StockStatus": product["stock_status"],
            "PricingStatus": product["pricing_status"],
            "Status": product["status"],
            "ProductType": product["product_type"],
            "IsActive": product["is_active"],
            "IsBundle": product["is_bundle"],
            "IsSimilar": product["is_similar"],
            "IsValidForExcelProcessing": product[
                "is_valid_for_excel_processing"
            ],
            "ManufacturerCorrected": product["manufacturer_corrected"],
            "EnergyStar": product["energy_star"],
            "Section508": product["section_508"],
            "EndUserInfo": product["end_user_info"],
            "Weight": product["weight"],
            "Height": product["height"],
            "Width": product["width"],
            "Length": product["length"],
            "Specification": product["specification"],
            "SearchableText": product["searchable_text"],
            "CreatedOn": product["created_on"],
            "UpdatedOn": product["updated_on"],
            "CategoryPath": product["category_path"],
            "AttributeTags": product["attribute_tags"],
            "Images": product["images"],
            "VendorInfo": product["vendor_info"],
            "Specifications": product["specifications"],
            "ManufacturerNamesSeen": product["manufacturer_names_seen"],
            "ValidationFlags": product["validation_flags"],
            "DataQualityFlag": product["data_quality_flag"],
            "raw_data": product["raw_data"],
        }

        actions.append(
            {
                "_index": INDEX_NAME,
                "_id": product["id"],
                "_source": document,
            }
        )

    if not actions:
        print("No products found.")
        return

    success, errors = helpers.bulk(
        es,
        actions,
        raise_on_error=False,
    )

    print(f"Successfully indexed: {success}")

    if errors:
        print(f"Indexing errors: {len(errors)}")
        for error in errors[:5]:
            print(error)
    else:
        print("No indexing errors.")


if __name__ == "__main__":
    main()

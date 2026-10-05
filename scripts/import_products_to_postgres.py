import json


import psycopg

import os

DATABASE_URL = os.environ["PRODUCT_RAG_DATABASE_URL"]

def main():
    # Load Elasticsearch backup
    with open("data/products_500_backup.txt", "r", encoding="utf-8") as file:
        data = json.load(file)

    hits = data["hits"]["hits"]

    print(f"Products found in backup: {len(hits)}")

    insert_query = """
        INSERT INTO products (
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
        )
        VALUES (
            %(id)s,
            %(name)s,
            %(description)s,
            %(manufacturer_id)s,
            %(manufacturer_name)s,
            %(category_id)s,
            %(category)s,
            %(axe_part_no)s,
            %(mfg_part_no)s,
            %(upc)s,
            %(list_price)s,
            %(regular_cost)s,
            %(quantity)s,
            %(stock_status)s,
            %(pricing_status)s,
            %(status)s,
            %(product_type)s,
            %(is_active)s,
            %(is_bundle)s,
            %(is_similar)s,
            %(is_valid_for_excel_processing)s,
            %(manufacturer_corrected)s,
            %(energy_star)s,
            %(section_508)s,
            %(end_user_info)s,
            %(weight)s,
            %(height)s,
            %(width)s,
            %(length)s,
            %(specification)s,
            %(searchable_text)s,
            %(created_on)s,
            %(updated_on)s,
            %(category_path)s,
            %(attribute_tags)s,
            %(images)s,
            %(vendor_info)s,
            %(specifications)s,
            %(manufacturer_names_seen)s,
            %(validation_flags)s,
            %(data_quality_flag)s,
            %(raw_data)s
        )
    """

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:

            for hit in hits:
                product = hit["_source"]

                record = {
                    "id": product.get("Id"),
                    "name": product.get("Name"),
                    "description": product.get("Description"),
                    "manufacturer_id": product.get("ManufacturerId"),
                    "manufacturer_name": product.get("ManufacturerName"),
                    "category_id": product.get("CategoryId"),
                    "category": product.get("Category"),
                    "axe_part_no": product.get("AXEPartNo"),
                    "mfg_part_no": product.get("MFGPartNo"),
                    "upc": product.get("UPC"),
                    "list_price": product.get("ListPrice"),
                    "regular_cost": product.get("RegularCost"),
                    "quantity": product.get("Quantity"),
                    "stock_status": product.get("StockStatus"),
                    "pricing_status": product.get("PricingStatus"),
                    "status": product.get("Status"),
                    "product_type": product.get("ProductType"),
                    "is_active": product.get("IsActive"),
                    "is_bundle": product.get("IsBundle"),
                    "is_similar": product.get("IsSimilar"),
                    "is_valid_for_excel_processing": product.get(
                        "IsValidForExcelProcessing"
                    ),
                    "manufacturer_corrected": product.get(
                        "ManufacturerCorrected"
                    ),
                    "energy_star": product.get("EnergyStar"),
                    "section_508": product.get("Section508"),
                    "end_user_info": product.get("EndUserInfo"),
                    "weight": product.get("Weight"),
                    "height": product.get("Height"),
                    "width": product.get("Width"),
                    "length": product.get("Length"),
                    "specification": product.get("Specification"),
                    "searchable_text": product.get("SearchableText"),
                    "created_on": product.get("CreatedOn"),
                    "updated_on": product.get("UpdatedOn"),
                    "category_path": json.dumps(product.get("CategoryPath")),
                    "attribute_tags": json.dumps(product.get("AttributeTags")),
                    "images": json.dumps(product.get("Images")),
                    "vendor_info": json.dumps(product.get("VendorInfo")),
                    "specifications": json.dumps(product.get("Specifications")),
                    "manufacturer_names_seen": json.dumps(
                        product.get("ManufacturerNamesSeen")
                    ),
                    "validation_flags": json.dumps(
                        product.get("ValidationFlags")
                    ),
                    "data_quality_flag": product.get("DataQualityFlag"),
                    "raw_data": json.dumps(product),
                }

                cursor.execute(insert_query, record)

    print(f"Successfully imported {len(hits)} products.")


if __name__ == "__main__":
    main()

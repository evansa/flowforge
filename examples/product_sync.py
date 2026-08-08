"""Example FlowForge product pipeline."""

from typing import Any

from flowforge import Pipeline

pipeline = Pipeline(
    name="product-sync",
    retries=3,
    retry_delay_seconds=0.1,
)


@pipeline.extract()
def extract_products() -> list[dict[str, Any]]:
    """Extract sample products."""
    return [
        {"product_id": "1001", "name": "Yamaha Keyboard", "barcode": "123456789"},
        {"product_id": "1002", "name": "Digital Piano", "barcode": "987654321"},
    ]


@pipeline.transform()
def transform_products(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Transform products for the target system."""
    return [{**product, "released": True} for product in products]


@pipeline.load()
def load_products(products: list[dict[str, Any]]) -> None:
    """Simulate loading products."""
    for product in products:
        print(f"Loading {product['product_id']} - {product['name']}")


if __name__ == "__main__":
    result = pipeline.run()
    print(f"Execution ID: {result.execution_id}")
    print(f"Status: {result.status}")
    print(f"Records: {result.records_processed}")

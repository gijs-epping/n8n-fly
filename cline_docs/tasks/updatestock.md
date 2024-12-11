Before you start read your instructions.

# Update stock import
Before we fetched stock from a csv but now it commes in from the API.

ENDPOINT: https://integrationgateway.onewaybike.nl/V1/012/Sales/CSStock?$top=20 

Ok can you read your instruction and start with the following task:

## Task:

1. import from api 
rewrite @/python/import_stock.py to fetch the results and add them to the database.


2. Use the database already available: currentstock
only store the sku and stock_shelf data.

- sku = Artikelcode 
- stock_shelf = Voorraad



3. Add top and skip to the cli params
Add the top and skip to the params so we can start the job if it fails. This can be implemented just like it is done in  @/python/open_orders.py



### endpoint result example:
{
    "d": {
        "results": [
            {
                "sku": "10002",
                "stock_qty": 33.0,
                "stock_ext": 0.0,
                "stock_shelf": 33.0
            },
            {
                "sku": "10003",
                "stock_qty": 105.0,
                "stock_ext": 0.0,
                "stock_shelf": 105.0
            },
            {
                "sku": "10004",
                "stock_qty": 22.0,
                "stock_ext": 0.0,
                "stock_shelf": 22.0
            },
            {
                "sku": "10006",
                "stock_qty": 33.0,
                "stock_ext": 0.0,
                "stock_shelf": 33.0
            },
            {
                "sku": "10007",
                "stock_qty": 10.0,
                "stock_ext": 0.0,
                "stock_shelf": 10.0
            },
            {
                "sku": "10008",
                "stock_qty": 18.0,
                "stock_ext": 0.0,
                "stock_shelf": 18.0
            },
            {
                "sku": "10009",
                "stock_qty": 50.0,
                "stock_ext": 0.0,
                "stock_shelf": 50.0
            },
            {
                "sku": "10010",
                "stock_qty": 20.0,
                "stock_ext": 0.0,
                "stock_shelf": 20.0
            },
            {
                "sku": "10011",
                "stock_qty": 19.0,
                "stock_ext": 0.0,
                "stock_shelf": 19.0
            },
            {
                "sku": "10012",
                "stock_qty": 53.0,
                "stock_ext": 0.0,
                "stock_shelf": 53.0
            },
            {
                "sku": "10013",
                "stock_qty": 25.0,
                "stock_ext": 0.0,
                "stock_shelf": 25.0
            },
            {
                "sku": "10014",
                "stock_qty": 42.0,
                "stock_ext": 0.0,
                "stock_shelf": 42.0
            },
            {
                "sku": "10015",
                "stock_qty": 37.0,
                "stock_ext": 0.0,
                "stock_shelf": 37.0
            },
            {
                "sku": "10016",
                "stock_qty": 38.0,
                "stock_ext": 0.0,
                "stock_shelf": 38.0
            },
            {
                "sku": "10017",
                "stock_qty": 38.0,
                "stock_ext": 6.0,
                "stock_shelf": 38.0
            },
            {
                "sku": "10018",
                "stock_qty": 28.0,
                "stock_ext": 0.0,
                "stock_shelf": 28.0
            },
            {
                "sku": "10019",
                "stock_qty": 19.0,
                "stock_ext": 0.0,
                "stock_shelf": 19.0
            },
            {
                "sku": "10020",
                "stock_qty": 33.0,
                "stock_ext": 0.0,
                "stock_shelf": 33.0
            },
            {
                "sku": "10021",
                "stock_qty": 44.0,
                "stock_ext": 0.0,
                "stock_shelf": 44.0
            },
            {
                "sku": "10023",
                "stock_qty": 231.0,
                "stock_ext": 0.0,
                "stock_shelf": 231.0
            }
        ]
    }
}

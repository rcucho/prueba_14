{
    'name': "Mstech Components",
    "category": "Product",
    'author': "Meditech",
    'summary':"Mstech MiPCLista",
    'depends': [
        'stock',
        'product',
        'sale',
        'mrp',
    ],
    'data': [
        'views/product_template.xml',
        'views/sale_order_line.xml',
        'security/ir.model.access.csv',
        'views/change_component.xml',
    ],
    'installable' : True,
    'auto_install' :  False,
    'application' :  False,
}

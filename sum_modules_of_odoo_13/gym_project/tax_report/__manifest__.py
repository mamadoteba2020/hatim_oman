# -*- coding: utf-8 -*-
{
    'name': "Tax Report",
    'summary': '''
        Tax Report (PDF and Excel Format)''',
    'description': '''
        Tax Report (PDF and Excel Format)
    ''',
    'author': 'DRC Systems India Pvt. Ltd.',
    'website': 'http://www.drcsystems.com',
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['account'],
    'images': ['static/description/output.gif'],
    'data': [
        'wizard/tax_report_view.xml',
        'report/report_tax_view.xml'
    ],
    'price': '50',
    'currency': 'EUR',
    'installable': True,
    'application': True,
}

# -*- coding: utf-8 -*-
# from odoo import http


# class FinancialCovenant15(http.Controller):
#     @http.route('/financial_covenant_15/financial_covenant_15', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/financial_covenant_15/financial_covenant_15/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('financial_covenant_15.listing', {
#             'root': '/financial_covenant_15/financial_covenant_15',
#             'objects': http.request.env['financial_covenant_15.financial_covenant_15'].search([]),
#         })

#     @http.route('/financial_covenant_15/financial_covenant_15/objects/<model("financial_covenant_15.financial_covenant_15"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('financial_covenant_15.object', {
#             'object': obj
#         })

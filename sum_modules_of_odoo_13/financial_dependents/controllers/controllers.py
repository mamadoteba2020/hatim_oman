# -*- coding: utf-8 -*-
# from odoo import http


# class FinancialDependents(http.Controller):
#     @http.route('/financial_dependents/financial_dependents/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/financial_dependents/financial_dependents/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('financial_dependents.listing', {
#             'root': '/financial_dependents/financial_dependents',
#             'objects': http.request.env['financial_dependents.financial_dependents'].search([]),
#         })

#     @http.route('/financial_dependents/financial_dependents/objects/<model("financial_dependents.financial_dependents"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('financial_dependents.object', {
#             'object': obj
#         })

# -*- coding: utf-8 -*-
# from odoo import http


# class ReturnSaleOrder(http.Controller):
#     @http.route('/return_sale_order/return_sale_order', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/return_sale_order/return_sale_order/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('return_sale_order.listing', {
#             'root': '/return_sale_order/return_sale_order',
#             'objects': http.request.env['return_sale_order.return_sale_order'].search([]),
#         })

#     @http.route('/return_sale_order/return_sale_order/objects/<model("return_sale_order.return_sale_order"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('return_sale_order.object', {
#             'object': obj
#         })

# -*- coding: utf-8 -*-
# from odoo import http


# class MySaleDiscount(http.Controller):
#     @http.route('/my_sale_discount/my_sale_discount', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/my_sale_discount/my_sale_discount/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('my_sale_discount.listing', {
#             'root': '/my_sale_discount/my_sale_discount',
#             'objects': http.request.env['my_sale_discount.my_sale_discount'].search([]),
#         })

#     @http.route('/my_sale_discount/my_sale_discount/objects/<model("my_sale_discount.my_sale_discount"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('my_sale_discount.object', {
#             'object': obj
#         })

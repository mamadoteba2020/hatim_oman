# -*- coding: utf-8 -*-
# from odoo import http


# class DigitTwo(http.Controller):
#     @http.route('/digit_two/digit_two', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/digit_two/digit_two/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('digit_two.listing', {
#             'root': '/digit_two/digit_two',
#             'objects': http.request.env['digit_two.digit_two'].search([]),
#         })

#     @http.route('/digit_two/digit_two/objects/<model("digit_two.digit_two"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('digit_two.object', {
#             'object': obj
#         })

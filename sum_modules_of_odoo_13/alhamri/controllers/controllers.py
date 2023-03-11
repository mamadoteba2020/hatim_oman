# -*- coding: utf-8 -*-
# from odoo import http


# class Alhamri(http.Controller):
#     @http.route('/alhamri/alhamri/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/alhamri/alhamri/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('alhamri.listing', {
#             'root': '/alhamri/alhamri',
#             'objects': http.request.env['alhamri.alhamri'].search([]),
#         })

#     @http.route('/alhamri/alhamri/objects/<model("alhamri.alhamri"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('alhamri.object', {
#             'object': obj
#         })

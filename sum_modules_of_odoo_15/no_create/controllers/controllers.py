# -*- coding: utf-8 -*-
# from odoo import http


# class NoCreate(http.Controller):
#     @http.route('/no_create/no_create', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/no_create/no_create/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('no_create.listing', {
#             'root': '/no_create/no_create',
#             'objects': http.request.env['no_create.no_create'].search([]),
#         })

#     @http.route('/no_create/no_create/objects/<model("no_create.no_create"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('no_create.object', {
#             'object': obj
#         })

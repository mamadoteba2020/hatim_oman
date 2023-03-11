# -*- coding: utf-8 -*-
# from odoo import http


# class StarsGym(http.Controller):
#     @http.route('/stars_gym/stars_gym/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stars_gym/stars_gym/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stars_gym.listing', {
#             'root': '/stars_gym/stars_gym',
#             'objects': http.request.env['stars_gym.stars_gym'].search([]),
#         })

#     @http.route('/stars_gym/stars_gym/objects/<model("stars_gym.stars_gym"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stars_gym.object', {
#             'object': obj
#         })

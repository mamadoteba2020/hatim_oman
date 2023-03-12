# -*- coding: utf-8 -*-
# from odoo import http


# class CostCar(http.Controller):
#     @http.route('/cost_car/cost_car', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cost_car/cost_car/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cost_car.listing', {
#             'root': '/cost_car/cost_car',
#             'objects': http.request.env['cost_car.cost_car'].search([]),
#         })

#     @http.route('/cost_car/cost_car/objects/<model("cost_car.cost_car"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cost_car.object', {
#             'object': obj
#         })

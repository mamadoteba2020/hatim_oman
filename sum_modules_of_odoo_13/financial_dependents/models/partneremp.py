from odoo import fields, models


class ResPartnerEmp_fin(models.Model):
    _inherit = 'res.partner'
    emp_tick = fields.Boolean(string='Employee')
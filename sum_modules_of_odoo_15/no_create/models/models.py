# from odoo import  models
from odoo import api,fields, models

class  AccountMove(models.Model):
    _inherit = 'account.move'




class SaleOrder(models.Model):
    _inherit = 'sale.order'

    



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'   



class Picking(models.Model):
    _inherit = 'stock.picking'
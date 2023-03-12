from odoo import api, fields, models, _





class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    #product_qty_two = fields.Float(string='Quantity', digits=(15,3), required=True)



class SaleOrder(models.Model):   
    _inherit = 'sale.order'




class AccountMove(models.Model):
    _inherit = 'account.move'
   
     
 

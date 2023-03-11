# -*- coding: utf-8 -*-
from odoo import models,api,fields
from odoo.exceptions import UserError, Warning

class AccountMoveHIC(models.Model):
    _inherit = 'account.move'
    consignee = fields.Char(string='Consignee Name')
    address_hic = fields.Text(string='Address')
    pin_code = fields.Char(string='Pin Code')
    tel_hic = fields.Char(string='Tel')
    itemqlist_id = fields.One2many('list.itemq','move_itemq_id', string='Item List')
    dmethod = fields.Many2one('delivery.method', string='Delivery Method')
    valueofgoods = fields.Char(string='Value Of Goods')
    qty_total = fields.Float(string="qty total", compute="_compute_totalqty")
    wight_total = fields.Float(string="qty total", compute="_compute_totalwight")
    # total_qty = fields.Float("Total Quintity", readonly=True, compute='_get_total_qty')

    # @api.onchange('itemqlist_id')
    # def _compute_totalqty(self):
    #     total_hic = 0.0
    #     if self.itemqlist_id:
    #         for i in self.itemqlist_id:
    #             if i.qty_itemq:
    #                 for m in i.qty_itemq:
    #                     total_hic+=m
    #     return  total_hic
    
    @api.depends('itemqlist_id')
    def _compute_totalwight(self):  
        for item in self:      
            w_total = 0.0       
            for line in item.itemqlist_id:      
                w_total += line.Wight_itemq 
        item.wight_total = w_total
    
    @api.depends('itemqlist_id')
    def _compute_totalqty(self):  
        for item in self:      
            q_total = 0.0       
            for line in item.itemqlist_id:      
                q_total += line.qty_itemq 
        item.qty_total = q_total
    # def _get_total_qty(self):
    #     for qty in self:
    #         total = 0.0
    #         for line in qty.itemqlist_id:
    #             total += line.qty_itemq  
    #     qty.total_qty = total

class ListItemq(models.Model):
    _name = 'list.itemq'
    _description = 'New Description'

    name = fields.Many2many("itemq.itemq","list_itemq_rel", "listt_id","itemq_id","Item") 
   
    move_itemq_id = fields.Many2one('account.move','Mo')
    
    
    qty_itemq = fields.Float(string='PCS.')
    Wight_itemq = fields.Float(string='Wight')
    




class Account_move_live_hic(models.Model):
    _inherit = 'account.move.line'


    


class ItemqItemq(models.Model):
    _name = 'itemq.itemq'
    _description = 'New Description'

    name = fields.Char(string='Item')




class DeliveryMethod(models.Model):
    _name = 'delivery.method'
    _description = 'New Description'

    name = fields.Char(string='Name Method')




class ResPartnerHic(models.Model):
    _inherit = 'res.partner'







#     @api.depends('order_line')
# def _commission_amount(self):
# for order in self:
# comm_total = 0.0
# for line in order.order_line:
# comm_total += line.commission_line 





    
    

    

   
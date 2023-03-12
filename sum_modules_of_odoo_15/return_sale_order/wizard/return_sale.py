# -*- coding: utf-8 -*-

from odoo import models,fields,api ,_
from datetime import datetime
from odoo.exceptions import UserError

class CreateReturnSale(models.TransientModel):
    _name = 'create.return.sale'
    _description = 'Create Return Sale Order'

    @api.model
    def default_get(self, fields_list):
        res = super(CreateReturnSale, self).default_get(fields_list)
        if 'my_sale_order_id' in fields_list:
            sale_order = self.env['sale.order'].browse(
                res['my_sale_order_id'])
            res['user_id'] = sale_order.user_id.id
            res['company_id'] = sale_order.company_id.id
            res['name_so'] = sale_order.name
        return res
    test = fields.Char(string="Test")
    user_id = fields.Many2one('res.users', string='Salesperson')
    company_id = fields.Many2one('res.company', 'Company',required=True,)
    return_line_my_id = fields.One2many(
        string='field_name',
        comodel_name='my.return.line',
        inverse_name='return_id_inv',
    )
    date_of_return = fields.Datetime(string="Date Of Return",
                                     default=datetime.today(),
                                     required=True)
    my_sale_order_id = fields.Many2one("sale.order")
    note = fields.Text()
    name_so = fields.Char(string="Sale Order")
    

    def open_sale_return(self):
        ctx = self.env.context.copy()
        ctx.update({
            'default_knk_sale_order_id': self.id,
            
        })
        return{
            'name': 'Returns',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.return.picking',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx
        }

    def return_wizard_so_cridet(self):
        return_lines = []
        for lines in self.return_line_my_id:
            return_lines.append((0, 0, {
                'my_product_id': lines.my_product_id.id,
                'my_product_qty': lines.my_product_qty,
                'reason_to_return': lines.reason_to_return
                }))
        addr = self.my_sale_order_id.partner_id.address_get(
            ['delivery', 'invoice'])
        return_order = {'partner_id': self.my_sale_order_id.partner_id.id,
                        'date_of_return': self.date_of_return,
                        'my_sale_order_id': self.my_sale_order_id.id,
                        'partner_invoice_id': addr['invoice'],
                        'partner_shipping_id': addr['delivery'],
                        'my_sale_order_return_line_ids': return_lines,
                        'note': self.note}
        return_order_id = self.env['sale.order.return'].create(return_order)
        return_order_id.button_confirm_two2()
    

    

    # def create_return_sale(self):
    #     print("hello")


    def return_wizard_so(self):
        return_lines = []
        for lines in self.return_line_my_id:
            return_lines.append((0, 0, {
                'my_product_id': lines.my_product_id.id,
                'my_product_qty': lines.my_product_qty,
                'reason_to_return': lines.reason_to_return
                }))
        addr = self.my_sale_order_id.partner_id.address_get(
            ['delivery', 'invoice'])
        return_order = {'partner_id': self.my_sale_order_id.partner_id.id,
                        'date_of_return': self.date_of_return,
                        'my_sale_order_id': self.my_sale_order_id.id,
                        'partner_invoice_id': addr['invoice'],
                        'partner_shipping_id': addr['delivery'],
                        'my_sale_order_return_line_ids': return_lines,
                        'note': self.note}
        return_order_id = self.env['sale.order.return'].create(return_order)
        return_order_id.button_confirm()

     
                    
            



class MyReturnLine(models.TransientModel):
    _name = 'my.return.line'

    return_id_inv = fields.Many2one('create.return.sale')
    my_product_id = fields.Many2one('product.product',
                                     string="Product",
                                     required="True")
    my_product_qty = fields.Float(string="Quantity")
    my_move_id = fields.Many2one('stock.move', "Move")
    reason_to_return = fields.Char(string="Reason")


    @api.onchange('return_id_inv')
    def _domain_change(self):
        domain = []
        for line in self.return_id_inv.my_sale_order_id.order_line:
            if line.qty_delivered > 0:
                domain.append(line.product_id.id)
        return {
            'domain': {
                'my_product_id': [('id', 'in', domain)]}
        }

    @api.onchange('my_product_qty')
    def check_quantity(self):
        for rec in self:
            lines = rec.return_id_inv.my_sale_order_id.order_line.filtered(
                lambda x: x.product_id == rec.my_product_id)
            for line in lines:
                if(rec.my_product_qty > line.my_balanced_qty or
                        rec.my_product_qty > line.qty_delivered):
                    raise UserError(
                        'Return quantity cannot be more than Delivered Quantity')

    @api.constrains('my_product_qty')
    def check_null_quantity(self):
        if self.my_product_qty <= 0:
            raise UserError('Return quantity must be atleast 1')
    
    
from odoo import api, fields, models
import odoo.addons.decimal_precision as dp




class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = amount_discount = 0.0
            for line in order.order_line:
                # line.price_subtotal = line.price_subtotal - (line.discount/100 * line.price_unit * line.product_qty)
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                amount_discount += (line.product_uom_qty * line.price_unit * line.discount) / 100
            order.update({
                'amount_untaxed_pu': amount_untaxed,
                'amount_tax_pu': amount_tax,
                'amount_discount_pu': amount_discount,
                'amount_total_pu': amount_untaxed + amount_tax,
            })
    
    

    discount_type_pu = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount type',
                                     readonly=False,
                                     default='percent')
    discount_rate_pu = fields.Float('Discount Rate', digits=dp.get_precision('Account'),
                                 readonly=False)
    amount_untaxed_pu = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax_pu = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all',
                                 track_visibility='always')
    amount_total_pu = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all',
                                   track_visibility='always')
    amount_discount_pu = fields.Monetary(string='Discount', store=True, readonly=True, compute='_amount_all',
                                      digits=dp.get_precision('Account'), track_visibility='always')

              
    @api.onchange('discount_type_pu', 'discount_rate_pu', 'order_line')
    def supply_rate(self):

        for order in self:
            if order.discount_type_pu == 'percent':
                for line in order.order_line:
                    line.discount = order.discount_rate_pu
            else:
                total = discount = 0.0
                for line in order.order_line:
                    total += round((line.product_uom_qty * line.price_unit))
                if order.discount_rate_pu != 0:
                    discount = (order.discount_rate_pu / total) * 100
                else:
                    discount = order.discount_rate_pu
                for line in order.order_line:
                    line.discount = discount
    
    def button_dummy(self):
        self.supply_rate()
        return True

    def _prepare_invoice(self, ):
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        if self.discount_type_pu=='percent':
            globaldis = 'percent'
        if self.discount_type_pu=='amount':
            globaldis = 'fixed'

        invoice_vals.update({
            'discount_type': self.discount_type_pu,
            'discount_rate': self.discount_rate_pu,
            # 'global_discount_type':globaldis,
            #  'tax_ids': [(6, 0, line.tax_ids.ids)],
            # 'invoice_line_ids': self.order_line.ids,
            # 'invoice_line_ids': [(1,0,{
            #                       'discount_type':globaldis,
            #                       'discount':self.order_line.discount,
            #                       })] 
            # 'invoice_line_ids.discount_type':globaldis,
            # 'invoice_line_ids.discount':self.order_line.discount,
        })
        return invoice_vals

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    discount = fields.Float(string='Discount (%)', digits=(16, 20), default=0.0)

    # in sale
    @api.depends('product_qty', 'discount', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.taxes_id.compute_all(price, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups('account.group_account_manager'):
                line.taxes_id.invalidate_cache(['invoice_repartition_line_ids'], [line.taxes_id.id])


    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line()
        res.update({
            'discount': self.discount,
           
            # 'global_discount_type':globaldis,
            #  'tax_ids': [(6, 0, line.tax_ids.ids)],
            # 'invoice_line_ids': self.order_line.ids,
            # 'invoice_line_ids': [(1,0,{
            #                       'discount_type':globaldis,
            #                       'discount':self.order_line.discount,
            #                       })] 
            # 'invoice_line_ids.discount_type':globaldis,
            # 'invoice_line_ids.discount':self.order_line.discount,
        })
        return res


    # in purchase
    # @api.depends('product_qty', 'price_unit', 'taxes_id')
    # def _compute_amount(self):
    #     for line in self:
    #         taxes = line.taxes_id.compute_all(**line._prepare_compute_all_values())
    #         line.update({
    #             'price_tax': taxes['total_included'] - taxes['total_excluded'],
    #             'price_total': taxes['total_included'],
    #             'price_subtotal': taxes['total_excluded'],
    #         })



    # def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        # self.ensure_one()
        # return {
        #     'price_unit': self.price_unit,
        #     'currency': self.order_id.currency_id,
        #     'quantity': self.product_qty,
        #     'product': self.product_id,
        #     'partner': self.order_id.partner_id,
        # }

from odoo import api, fields, models, _,tools
import time
import base64
from datetime import  datetime,date, timedelta
from odoo.exceptions import Warning

class SubscriptionConversion(models.Model):
    _name = 'subscription.conversion'
    _description = 'New Description'
    _rec_name ='sud_conv_seq'
    sud_conv_seq = fields.Char(string='Subscriptions Conversion No',readonly=True)
    ref_seq_sub = fields.Char(string='Reference Subscriptions')
    state = fields.Selection([
        ('active', 'active'),
        ('hold', 'Hold'),
        ('not_subscribed', 'Not subscribed'),
        ('cancel', 'Cancelled'),], string='Status', readonly=True, copy=False, index=True,default='active')
    current_subscriber = fields.Many2one('res.partner', string='Current Subscriber',required=True)
    converted_subscriber = fields.Many2one('res.partner', string='Converted Subscriber',required=True)
    start_date_conv = fields.Date(string='Start Date',required=True)
    end_date_conv = fields.Date(string='End date',state={'hold': [('required', False)]})
    add_field_conv = fields.Float(string='الاشتراك بالأيام',default=1.0)
    difrinet_conv = fields.Integer(string='عدد الأيام المتبقية')
    line_sub_id_conv = fields.One2many(comodel_name='subscriptions.line.conv',inverse_name='subscriptions_main_conv', string='Line')
    inv_count_conv = fields.Float(compute='_invs_counted',string='Invoice')
    image_conv = fields.Binary(related="current_subscriber.image_1920", attachment=True)
    color_conv = fields.Integer(string='Color Index')
    mobile_star_conv = fields.Char(related="current_subscriber.mobile",string="Mobile",required=True)

    def stop_sub_conv(self):
        if self.start_date_conv and self.end_date_conv:
            self.state = 'hold'
            now_conv = datetime.now() + timedelta(days=1)
            date_now_conv = now_conv.date()
            day_stop_conv = self.end_date_conv - date_now_conv
            self.difrinet_conv = day_stop_conv.days
            self.end_date_conv = None

    def start_hold_sub_conv(self):  
        if self.start_date_conv and self.difrinet_conv:
            now_conv = datetime.now() + timedelta(days=1)
            date_now_conv = now_conv.date()
            self.end_date_conv = timedelta(days=self.difrinet_conv) + date_now_conv
            self.state = 'active'

    def non_subscription_cron_conv(self):
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        date_now_2 = fields.Date.from_string(date_now)
        match = self.search([])
        for i in match:
            if i.state =='active':
                if i.end_date_conv:
                    end_date_new = fields.Date.from_string(i.end_date_conv)
                    if date_now_2 >= end_date_new:
                        i.state = 'not_subscribed'
    
    @api.onchange('end_date_conv')
    def change_end_date_conv(self):
        if self.start_date_conv:
            day_total = self.end_date_conv - self.start_date_conv
            self.add_field_conv = day_total.days

    @api.onchange('add_field')
    def change_date_conv(self):
        if self.start_date_conv and self.add_field_conv:
            self.end_date_conv = timedelta(days=self.add_field_conv) + self.start_date_conv


    def active_def_conv(self):
        self.state = 'active'
        
    def cancel_def_conv(self):
        self.state = 'cancel'

    @api.model
    def create(self,vals):
        seq = self.env['ir.sequence'].next_by_code('subscription.conversion') or '/'
        vals['sud_conv_seq'] = seq
        res = super(SubscriptionConversion,self).create(vals)
        return res

    def _invs_counted(self):
        for each in self:
            invs_ids = self.env['account.move'].sudo().search([('rega_ref', '=', each.id)])
            each.inv_count_conv = len(invs_ids)
    
    def create_invoice_conv(self):
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        invoice_obj = self.env["account.move"]
        invoice_line_obj = self.env["account.move.line"]
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        prd_account_id = journal.default_credit_account_id.id
        for subs in self:
            if subs.current_subscriber:
                curr_invoice = {
                    'partner_id': subs.current_subscriber.id,
                    'state': 'draft',
                    'type': 'out_invoice',
                    'invoice_date': date_now,
                    'invoice_origin': "Subscription# : " + subs.sud_conv_seq,
                    'ref': "Subscription# : " + subs.sud_conv_seq,
                    'rega_ref':subs.id,
                 
                }
                inv_ids = invoice_obj.create(curr_invoice)
                inv_id = inv_ids.id

                if inv_ids:
                    journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
                    prd_account_id = journal.default_credit_account_id.id
                    list_value = []
                    if subs.line_sub_id_conv:
                        for line in subs.line_sub_id_conv:
                            list_value.append((0,0, {
                                        'product_id':line.prod_sub_conv.id,
                                        'name': line.prod_sub_conv.name,
                                        'price_unit': line.price_sub_conv,
                                        'quantity': 1.0,
                                        'account_id': prd_account_id,
                                        'move_id': inv_id,
                                    }))
                        print(list_value)
                        inv_ids.write({'invoice_line_ids': list_value})
                          
                        self.state = 'active'
                        view_id = self.env.ref('account.view_move_form').id
                        return {
                                'view_mode': 'form',
                                'res_model': 'account.move',
                                'view_id': view_id,
                                'type': 'ir.actions.act_window',
                                'name': _('Gym Convert Invoices'),
                                 'res_id': inv_id}


    def invs_view(self):
        self.ensure_one()
        domain = [('rega_ref', '=', self.id),('type', '=', 'out_invoice')]
        return {
            'name': _('Invoices Reg'),
            'domain': domain,  
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Invoce
                        </p>'''),
            'limit': 80,
            'context': "{'default_rega_ref': '%s'}" % self.id
        }



class SubscriptionsLineConv(models.Model):
    _name = 'subscriptions.line.conv'
    _description = 'New Description'

    prod_sub_conv = fields.Many2one(comodel_name='product.template', string='Packages',required=True)
    quin_sub_conv = fields.Char(string='Quantities',default='1')
    price_sub_conv = fields.Char(string='Price')
    subscriptions_main_conv = fields.Many2one(comodel_name='subscription.conversion', string='subscriptions_main')
    # price_sub = fields.Monetary(string="Price")
    @api.onchange('prod_sub_conv')
    def onchange_prod_sub_conv(self):
        self.price_sub_conv = self.prod_sub_conv.list_price
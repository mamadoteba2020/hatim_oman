# -*- coding: utf-8 -*-
from odoo import api, fields, models, _,tools
import time
import base64
from datetime import  datetime,date, timedelta
from odoo.exceptions import Warning



class AccountMoveSub(models.Model):
    _inherit = 'account.move'
    rega_ref = fields.Many2one('subscriptions.subscriptions', invisible=1, copy=False)


class ModuleSubscriptions(models.Model):
    _name = 'subscriptions.subscriptions'
    _description = 'New Description'
    _rec_name ='sub_seq'
    sub_seq = fields.Char(string='Subscriptions No',readonly=True)
    state = fields.Selection([
        ('draft', 'draft'),
        ('active', 'active'),
        ('hold', 'Hold'),
        ('not_subscribed', 'Not subscribed'),
        ('cancel', 'Cancelled'),], string='Status', readonly=True, copy=False, index=True,default='draft')
    res_subscription = fields.Many2one('res.partner', string='Subscriber',required=True)
    start_date = fields.Date(string='Start Date',required=True)
    end_date = fields.Date(string='End date',state={'hold': [('required', False)]})
    line_sub_id = fields.One2many(comodel_name='subscriptions.line',inverse_name='subscriptions_main', string='Line')
    inv_count = fields.Float(compute='_invs_counted',string='Invoice')
    image = fields.Binary(related="res_subscription.image_1920", attachment=True)
    color = fields.Integer(string='Color Index')
    mobile_star = fields.Char(related="res_subscription.mobile",string="Mobile",required=True)
    add_field = fields.Float(string='الاشتراك بالأيام',default=1.0)
    difrinet = fields.Integer(string='عدد الأيام المتبقية')
    legend_blocked = fields.Char(
        'Red Kanban Label', default=lambda s: _('not_subscribed'), translate=True, required=True,
        help='Override the default value displayed for the blocked state for kanban selection, when the task or issue is in that stage.')
    legend_done = fields.Char(
        'Green Kanban Label', default=lambda s: _('active'), translate=True, required=True,
        help='Override the default value displayed for the done state for kanban selection, when the task or issue is in that stage.')
    legend_normal = fields.Char(
        'Grey Kanban Label', default=lambda s: _('draft'), translate=True, required=True,
        help='Override the default value displayed for the normal state for kanban selection, when the task or issue is in that stage.')
    
          
            

    def non_subscription_cron(self):
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        date_now_2 = fields.Date.from_string(date_now)
        match = self.search([])
        for i in match:
            if i.state =='active':
                if i.end_date:
                    end_date_new = fields.Date.from_string(i.end_date)
                    if date_now_2 >= end_date_new:
                        i.state = 'not_subscribed'

    def stop_sub(self):
        if self.start_date and self.end_date:
            self.state = 'hold'
            now = datetime.now() + timedelta(days=1)
            date_now = now.date()
            day_stop = self.end_date - date_now
            self.difrinet = day_stop.days
            self.end_date = None 
    
    def start_hold_sub(self):  
        if self.start_date and self.difrinet: 
            now = datetime.now() + timedelta(days=1)
            date_now = now.date()
            self.end_date = timedelta(days=self.difrinet) + date_now
            self.state = 'active'
    
    def active_def(self):
        self.state = 'active'
       
    def cancel_def(self):
        self.state = 'cancel'

    @api.onchange('end_date')
    def change_end_date(self):
        if self.start_date:
            day_total = self.end_date - self.start_date
            self.add_field = day_total.days



    @api.onchange('add_field')
    def change_date(self):
        # fielddate = datetime.strptime(self.add_field, '%d%m%Y').date()
        if self.start_date and self.add_field:
            # self.end_date = (datetime.strptime(self.start_date, '%Y-%m-%d')+relativedelta(days =+ self.add_field))
            self.end_date = timedelta(days=self.add_field) + self.start_date
    


    @api.model
    def create(self,vals):
       
        seq = self.env['ir.sequence'].next_by_code('subscriptions.subscriptions') or '/'
        vals['sub_seq'] = seq
        res = super(ModuleSubscriptions,self).create(vals)
        return res

    
    def _invs_counted(self):
        for each in self:
            invs_ids = self.env['account.move'].sudo().search([('rega_ref', '=', each.id)])
            each.inv_count = len(invs_ids)

    def create_invoice(self):
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        invoice_obj = self.env["account.move"]
        invoice_line_obj = self.env["account.move.line"]
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        prd_account_id = journal.default_credit_account_id.id
        for subs in self:
            if subs.res_subscription:
                curr_invoice = {
                    'partner_id': subs.res_subscription.id,
                    'state': 'draft',
                    'type': 'out_invoice',
                    'invoice_date': date_now,
                    'invoice_origin': "Subscription# : " + subs.sub_seq,
                    'ref': "Subscription# : " + subs.sub_seq,
                    'rega_ref':subs.id,
                }
                inv_ids = invoice_obj.create(curr_invoice)
                inv_id = inv_ids.id

                if inv_ids:
                    journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
                    prd_account_id = journal.default_credit_account_id.id
                    list_value = []
                    if subs.line_sub_id:
                        for line in subs.line_sub_id:
                            list_value.append((0,0, {
                                        'product_id':line.prod_sub.id,
                                        'name': line.prod_sub.name,
                                        'price_unit': line.price_sub,
                                        'quantity': 1.0,
                                        'account_id': prd_account_id,
                                        'move_id': inv_id,
                                    }))
                        print(list_value)
                        inv_ids.write({'invoice_line_ids': list_value})
                        self.state = 'active'
                        self.line_sub_id = None
                        view_id = self.env.ref('account.view_move_form').id
                        return {
                                'view_mode': 'form',
                                'res_model': 'account.move',
                                'view_id': view_id,
                                'type': 'ir.actions.act_window',
                                'name': _('Gym Invoices'),
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

    #  def open_tracebility(self):

    # res = self.env['ir.actions.act_window'].for_xml_id('custom_module_name', 'wizard_action')

    # return res
       


class ModuleSubscriptionsLine(models.Model):
    _name = 'subscriptions.line'
    _description = 'New Description'
    prod_sub = fields.Many2one(comodel_name='product.template', string='Packages',required=True)
    quin_sub = fields.Char(string='Quantities',default='1')
    price_sub = fields.Char(string='Price')
    subscriptions_main = fields.Many2one(comodel_name='subscriptions.subscriptions', string='subscriptions_main')

    @api.onchange('prod_sub')
    def onchange_prod_sub(self):
        self.price_sub = self.prod_sub.list_price
    

    
    



    

   



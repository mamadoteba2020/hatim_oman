from odoo import api, fields, models,_
import time
import base64
from datetime import  datetime,date, timedelta
from odoo.exceptions import Warning

class ConvSubWiz(models.TransientModel):
    _name = 'conv.sub.wiz'
    _description = 'Create convert sub'
    res_sub_conv_wiz = fields.Many2one('res.partner', string='Convert To',required=True)
    subscription_code = fields.Many2one('subscriptions.subscriptions', string='رقم الاشتراك')
    
    
    def conv_sub(self):
        print("hello")
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        subscriptions_obj = self.env["subscription.conversion"]
        subscriptions_line_obj = self.env["subscriptions.line.conv"]


       
        for subs in self:
            if subs.subscription_code:
                curr_subscription = {
                    'current_subscriber': self.res_sub_conv_wiz.id,
                    'converted_subscriber': subs.subscription_code.res_subscription.id,
                    'state':subs.subscription_code.state,
                    'ref_seq_sub':subs.subscription_code.sub_seq,
                    # 'type': 'out_invoice',
                    'start_date_conv': subs.subscription_code.start_date,
                    'end_date_conv': subs.subscription_code.end_date,
                    'add_field_conv': subs.subscription_code.add_field,
                    'difrinet_conv': subs.subscription_code.difrinet,
                    'image_conv': subs.subscription_code.image,
                    'color_conv': subs.subscription_code.color,
                    'mobile_star_conv': subs.subscription_code.mobile_star
                  
                }
                sub_ids = subscriptions_obj.create(curr_subscription)
                sub_id = sub_ids.id

                if sub_ids:
                    
                    list_value = []
                    if subs.subscription_code.line_sub_id:
                        for line in subs.subscription_code.line_sub_id:
                            list_value.append((0,0, {
                                        'prod_sub_conv':line.prod_sub.id,
                                        # 'name': line.prod_sub.name,
                                        # 'price_unit': line.price_sub,
                                        'quin_sub_conv': 1.0,
                                        'price_sub_conv': line.price_sub,
                                        # 'move_id': inv_id,
                                    }))
                        print(list_value)
                        sub_ids.write({'line_sub_id_conv': list_value})
                        # self.state = 'active'
                        # self.line_sub_id = None
                        view_id = self.env.ref('stars_gym.model_subscriptions_subscriptions_view_form').id
                        return {
                                'view_mode': 'form',
                                'res_model': 'subscriptions.subscriptions',
                                'view_id': view_id,
                                'type': 'ir.actions.act_window',
                                'name': _('Gym Subscription'),
                                 'res_id': sub_id}
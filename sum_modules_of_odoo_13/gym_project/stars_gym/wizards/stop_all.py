from odoo import api, fields, models,_
import time
import base64
from datetime import  datetime,date, timedelta
from odoo.exceptions import Warning

class ConvSubWiz(models.Model):
    _name = 'stopall.sub.wiz'
    new_field = fields.Char(string='new_field')
    # stop_subs_id = fields.Many2one('subscriptions.subscriptions', string='subscriptions')
    open_stop = fields.Boolean(string='open_stop' ,default=False)
    def stopall_sub(self):
        self.open_stop = True
        stopsub_obj = self.env["subscriptions.subscriptions"].sudo().search([])
        # stopsub_records = self.env['subscriptions.subscriptions'].sudo().search([])
        for i in stopsub_obj:
            if i.end_date:
                if i.state == 'active':
                    i.state = 'hold'
                    now = datetime.now() + timedelta(days=1)
                    date_now = now.date()
                    day_stop = i.end_date - date_now
                    i.difrinet = day_stop.days
                    i.end_date = None 
        


   

        # existing_records = self.env['hr.overtime'].sudo().search([]).attendance_id.ids
        # print("alllllll",existing_records)
        # overtime_records = self.env['hr.attendance'].sudo().search([])
        # overtime_records_ids = self.sudo().search([('id', 'not in', existing_records)])
        # print(overtime_records_ids)
        # for rec in overtime_records_ids:
        #     overtime_amount = rec.sudo().overtime_amount
        #     if overtime_amount > 0 and rec.employee_id.contract_id.state == 'open':
        #         print("osman" * 10, rec.employee_id.name,rec.id)
        #         self.env['hr.overtime'].sudo().create({
        #             'employee_id': rec.employee_id.id,
        #             'department_id': rec.employee_id.department_id.id,
        #             'contract_id': rec.employee_id.contract_id.id,
        #             'type': 'cash',
        #             'duration_type': 'hours',
        #             # 'payslip_paid': True,
        #             'days_no_tmp': rec.overtime_amount,
        #             'state': 'draft',
        #             'attendance_id': rec.id,
        #         })
        #   def update_employee_status(self):
        # resignation = self.env['hr.resignation'].search([('state', '=', 'approved')])
        # for rec in resignation:
        #     pass
            # if rec.expected_revealing_date <= fields.Date.today() and rec.employee_id.active:
            #     rec.employee_id.active = False
            #     # Changing fields in the employee table with respect to resignation
            #     rec.employee_id.resign_date = rec.expected_revealing_date
            #     if rec.resignation_type == 'resigned':
            #         rec.employee_id.resigned = True
            #     else:
            #         rec.employee_id.fired = True
            #     # Removing and deactivating user
            #     if rec.employee_id.user_id:
            #         rec.employee_id.user_id.active = False
            #         rec.employee_id.user_id = None

            #_____________________
        #       existing_records = self.env['late.check_in'].sudo().search([]).attendance_id.ids

        # minutes_after = int(self.env['ir.config_parameter'].sudo().get_param('late_check_in_after')) or 0
        # max_limit = int(self.env['ir.config_parameter'].sudo().get_param('maximum_minutes')) or 0
        # late_check_in_ids = self.sudo().search([('id', 'not in', existing_records)])
        # print("osman"*10,late_check_in_ids)
        # for rec in late_check_in_ids:
        #     late_check_in = rec.sudo().late_check_in
        #     print("rec.let",rec.late_check_in , minutes_after ,late_check_in,max_limit)
        #     if rec.late_check_in :
        #         # > minutes_after and late_check_in > minutes_after and late_check_in < max_limit:
        #         print("osman" * 10)
        #         print(self.env['late.check_in'].sudo().create({
        #             'employee_id': rec.employee_id.id,
        #             'late_minutes': late_check_in,
        #             'date': rec.check_in.date(),
        #             'attendance_id': rec.id,
        #         }))
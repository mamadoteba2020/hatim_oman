
#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
import base64
"""
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import xlwt
"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
#from odoo.addons.website.models.website import slug


class TaxReport(models.TransientModel):
    _name = "tax.report"
    _description = "Tax Report"

    date_from = fields.Date()
    date_to = fields.Date()
    target_moves = fields.Selection([('all_entries', 'All Entries'), ('all_posted', 'All Posted Entries')],
                                    'Target Moves', default='all_posted')

    qs = fields.Selection([('q1', 'Q1'), ('q2', 'Q2'), ('q3', 'Q3'), ('q4', 'Q4')], 'Tax Period', default='q1')
    
    report_typ_1 = fields.Selection([('view', 'View'), ('print', 'Print')],
                                    'View or Print', default='print')
    # report_for = fields.Selection([('all', 'All Taxes'), ('manual', 'Manual Selection')], 'Tax Report', default='all')
    # display_detail = fields.Boolean('Display Detail')
    tax_ids = fields.Many2many('account.tax', string='Taxes',
                               default=lambda self: self.env['account.tax'].search([('active', '=', True)]))

    @api.onchange('qs')
    def _compute_qs_bc(self):
        if self.qs == 'q1':
            self.date_from = datetime.strptime("01/01"+"/"+str(date.today().year), '%d/%m/%Y')
            self.date_to = datetime.strptime("31/03"+"/"+str(date.today().year), '%d/%m/%Y')
        if self.qs == 'q2':
            self.date_from = datetime.strptime("01/04"+"/"+str(date.today().year), '%d/%m/%Y')
            self.date_to = datetime.strptime("30/06"+"/"+str(date.today().year), '%d/%m/%Y')
        if self.qs == 'q3':
            self.date_from = datetime.strptime("01/07"+"/"+str(date.today().year), '%d/%m/%Y')
            self.date_to = datetime.strptime("30/09"+"/"+str(date.today().year), '%d/%m/%Y')
        if self.qs == 'q4':
            self.date_from = datetime.strptime("01/10"+"/"+str(date.today().year), '%d/%m/%Y')
            self.date_to = datetime.strptime("31/12"+"/"+str(date.today().year), '%d/%m/%Y')
        

    def print_report_details(self):
        d1 = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'target_moves': self.target_moves,
            'tax_ids': self.tax_ids.ids,
        }
        d = self.get_data_detailed(d1)
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'target_moves': self.target_moves,
            'tax_ids': self.tax_ids.ids,
            'ids': self.ids,
            'model': self._name,
            'report_typ_1': self.report_typ_1,
            
            'report_total': d['report_total'],
            'report_total_1': d['report_total_1'],
            'report_total_2': d['report_total_2'],
            'report_total_4': d['report_total_4'],
            's1': d['s1'],
            's2': d['s2'],
            's3': d['s3'],
            's1_r': d['s1_r'],
            's2_r': d['s2_r'],
            's3_r': d['s3_r'],
            'p1': d['p1'],
            'p2': d['p2'],
            'p3': d['p3'],
            'p1_pr': d['p1_pr'],
            'p2_pr': d['p2_pr'],
            'p3_pr': d['p3_pr'],
        }
        return self.env.ref('tax_report.action_report_tax_report_detailed').report_action(self, data=data) 
    
    #@api.multi
    def print_report(self):
        d1 = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'target_moves': self.target_moves,
            'tax_ids': self.tax_ids.ids,
        }
        d = self.get_data_1(d1)
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'target_moves': self.target_moves,
            'tax_ids': self.tax_ids.ids,
            'ids': self.ids,
            'model': self._name,
            'report_typ_1': self.report_typ_1,
            
            'report_total': d['report_total'],
            'report_total_1': d['report_total_1'],
            'report_total_2': d['report_total_2'],
            'report_total_4': d['report_total_4'],
            'tot': d['tot'],

            'sale': d['sale'],
            'purchase': d['purchase'],

            'sale_tot': d['sale_tot'],
            'purchase_tot': d['purchase_tot'],

            'ss_ref': d['ss_ref'],
            'ss_ref_tot': d['ss_ref_tot'],
            'pp_ref': d['pp_ref'],
            'pp_ref_tot': d['pp_ref_tot'],
        }
        return self.env.ref('tax_report.action_report_tax_report').report_action(self, data=data) 

    #@api.multi
    def print_report_view(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'target_moves': self.target_moves,
            'tax_ids': self.tax_ids.ids,
            'ids': self.ids,
            'model': self._name,
            'report_typ_1': self.report_typ_1,
        }
        [action] = self.env.ref('tax_report.action_move_journal_line_1').read()
        action['domain'] = [["id", "in", self.get_data_1(data)['total_sale_rep']]]
        action['target'] = "current"
        return action

    def get_data_1(self, data):
        s_tax = p_tax = s_tax_tot = p_tax_tot = ss_ref = pp_ref = ss_ref_tot = pp_ref_tot = 0.0
        total_sale_rep = []

        report_total = []
        report_total_1 = []
        report_total_2 = []
        report_total_4 = []

        for tax in self.env['account.tax'].search([('id', 'in', data['tax_ids']), ('active', '=', True)]):
            base_sale = base_purchase = sale_tax = purchase_tax = s_ref = p_ref = 0.0
             
            mv = self.env['account.move.line'].search(
                [('date', '>=', data['date_from']), ('date', '<=', data['date_to']),
                 ('tax_line_id', '=', tax.id)])
            if data['target_moves'] == 'all_posted':
                mv = self.env['account.move.line'].search(
                    [('date', '>=', data['date_from']), ('date', '<=', data['date_to']), ('tax_line_id', '=', tax.id),
                     ('move_id.state', '=', 'posted')])

            if mv:
                for n in mv:
                    if tax.type_tax_use == 'sale':
                        total_sale_rep.append(n.id)
                        sale_tax += n.credit
                        s_tax += n.credit
                        base_sale += n.credit * 100 / tax.amount
                        s_tax_tot += n.credit * 100 / tax.amount

                        if n.move_id.type == 'out_refund':
                            s_ref += n.debit
                            ss_ref += n.debit
                            ss_ref_tot += n.debit * 100 / tax.amount
                    elif tax.type_tax_use == 'purchase':
                        total_sale_rep.append(n.id)
                        purchase_tax += n.debit
                        p_tax += n.debit
                        base_purchase += n.debit * 100 / tax.amount
                        p_tax_tot += n.debit * 100 / tax.amount

                        if n.move_id.type == 'in_refund':
                            p_ref += n.credit
                            pp_ref += n.credit
                            pp_ref_tot += n.credit * 100 / tax.amount

            if tax.type_tax_use == 'sale' and mv:
                sig = 0
                if report_total:
                    
                    for s in report_total:
                        if s['per'] == tax.amount:
                            sig = 1
                            s['base_sale'] = round(s['base_sale'] + abs(base_sale), 2)
                            s['sale_tax'] = round(s['sale_tax'] + abs(sale_tax), 2)
                            s['s_ref'] = round(s['s_ref'] + abs(s_ref), 2)
                            s['s_ref_base'] = round(s['s_ref_base'] + abs(s_ref * 100 / tax.amount), 2)
                if sig == 0:
                    report_total.append({'tax_name':_("Sales With Base Percentage VAT ") + str(tax.amount), 'base_sale': round(abs(base_sale), 2), 'sale_tax': round(abs(sale_tax), 2), 's_ref': round(abs(s_ref), 2), 's_ref_base': round(abs(s_ref * 100 / tax.amount), 2), 'per': tax.amount})
            elif tax.type_tax_use == 'purchase' and mv:
                sig = 0
                if report_total_1:
                    
                    for s in report_total_1:
                        if s['per'] == tax.amount:
                            sig = 1
                            s['base_purchase'] = round(s['base_purchase'] + abs(base_purchase), 2)
                            s['purchase_tax'] = round(s['purchase_tax'] + abs(purchase_tax), 2)
                            s['p_ref'] = round(s['p_ref'] + abs(p_ref), 2)
                            s['p_ref_base'] = round(s['p_ref_base'] + abs(p_ref * 100 / tax.amount), 2)
                if sig == 0:
                    report_total_1.append({'tax_name': _("Purchase With Base Percentage VAT ") + str(tax.amount), 'base_purchase': round(abs(base_purchase), 2), 'purchase_tax': round(abs(purchase_tax), 2), 'p_ref': round(abs(p_ref), 2), 'p_ref_base': round(abs(p_ref * 100 / tax.amount), 2), 'per': tax.amount})
        fin_tot = (abs(s_tax) - abs(ss_ref)) - (abs(p_tax) - abs(pp_ref))
        return {
            'total_sale_rep': total_sale_rep,
            
            'report_total': report_total,
            'report_total_1': report_total_1,
            'report_total_2': report_total_2,
            'report_total_4': report_total_4,
            'tot': format(round(fin_tot, 2), ","),

            'sale': format(round(abs(s_tax), 2), ","),
            'purchase': format(round(abs(p_tax), 2), ","),

            'sale_tot': format(round(abs(s_tax_tot), 2), ","),
            'purchase_tot': format(round(abs(p_tax_tot), 2), ","),

            'ss_ref': format(round(ss_ref, 2), ","),
            'ss_ref_tot': format(round(ss_ref_tot, 2), ","),
            'pp_ref': format(round(pp_ref, 2), ","),
            'pp_ref_tot': format(round(pp_ref_tot, 2), ","),
            
        }

    def get_data_detailed(self, data):
        
        
        report_total = []
        report_total_1 = []
        report_total_2 = []
        report_total_4 = []
        s1 = s2 = s3 = s1_r = s2_r = s3_r = p1 = p2 = p3 = p1_pr = p2_pr = p3_pr = 0.0
        
        for tax in self.env['account.tax'].search([('id', 'in', data['tax_ids']), ('active', '=', True)]):
            #s_base_total = s_tax_total = s_total = p_base_total = p_tax_total = p_total = 0.0
            mv = self.env['account.move.line'].search(
                [('date', '>=', data['date_from']), ('date', '<=', data['date_to']),
                 ('tax_line_id', '=', tax.id)])
            #print inv and bill
            #print inv
            if data['target_moves'] == 'all_posted':
                mv = self.env['account.move.line'].search(
                    [('date', '>=', data['date_from']), ('date', '<=', data['date_to']), ('tax_line_id', '=', tax.id),
                     ('move_id.state','=','posted'),('move_id.name','=like','INV%')])
            if mv:
                for n in mv:
                    if tax.type_tax_use == 'sale':
                        desc = n.name
                        partner = n.partner_id.name
                        vat_no = n.partner_id.vat
                        inv_date = n.date
                        inv_no = n.move_id.name
                        s_base_total = n.balance * 100 / tax.amount
                        s1 += n.balance * 100 / tax.amount
                        s_tax_total = n.balance
                        s2 += n.balance
                        s_total = (n.balance * 100 / tax.amount) + n.balance
                        s3 += s_total
                        report_total.append({'desc': desc,
                                             'partner': partner,
                                             'vat_no': vat_no, 
                                             'inv_date': inv_date,
                                             'inv_no': inv_no,
                                             's_base_total': format(round(abs(s_base_total), 2), ","), 
                                             's_tax_total': format(round(abs(s_tax_total), 2), ","),
                                             's_total': format(round(abs(s_total), 2), ","),
                                             'per': tax.amount})
            mv = self.env['account.move.line'].search(
                [('date', '>=', data['date_from']), ('date', '<=', data['date_to']),
                 ('tax_line_id', '=', tax.id)])
            #print inv and bill
            #print inv
            if data['target_moves'] == 'all_posted':
                mv = self.env['account.move.line'].search(
                    [('date', '>=', data['date_from']), ('date', '<=', data['date_to']), ('tax_line_id', '=', tax.id),
                     ('move_id.state','=','posted'),('move_id.name','=like','POSS%')])
            if mv:
                for n in mv:
                    if tax.type_tax_use == 'sale':
                        desc = n.name
                        partner = n.partner_id.name
                        vat_no = n.partner_id.vat
                        inv_date = n.date
                        inv_no = n.move_id.name
                        s_base_total = n.balance * 100 / tax.amount
                        s1 += n.balance * 100 / tax.amount
                        s_tax_total = n.balance
                        s2 += n.balance
                        s_total = (n.balance * 100 / tax.amount) + n.balance
                        s3 += s_total
                        report_total.append({'desc': desc,
                                             'partner': partner,
                                             'vat_no': vat_no, 
                                             'inv_date': inv_date,
                                             'inv_no': inv_no,
                                             's_base_total': format(round(abs(s_base_total), 2), ","), 
                                             's_tax_total': format(round(abs(s_tax_total), 2), ","),
                                             's_total': format(round(abs(s_total), 2), ","),
                                             'per': tax.amount})
            #print bill
            mvp = self.env['account.move.line'].search(
                [('date', '>=', data['date_from']), ('date', '<=', data['date_to']),
                 ('tax_line_id', '=', tax.id)])
            if data['target_moves'] == 'all_posted':
                mvp = self.env['account.move.line'].search(
                    [('date', '>=', data['date_from']), ('date', '<=', data['date_to']), ('tax_line_id', '=', tax.id),
                     ('move_id.state','=','posted'),('move_id.name','=like','BILL%')])
            if mvp:
                for n in mvp:
                    if tax.type_tax_use == 'purchase':
                        desc_p = n.name
                        partnerp = n.partner_id.name
                        vat_no_p = n.partner_id.vat
                        inv_date_p = n.date
                        inv_nop = n.move_id.name
                        p_base_total_p = n.balance * 100 / tax.amount
                        p1 += n.balance * 100 / tax.amount
                        p_tax_total_p = n.balance
                        p2 += n.balance
                        p_total = (n.balance * 100 / tax.amount) + n.balance
                        p3 += p_total

                        report_total_1.append({'desc_P': desc_p,
                                               'partner_p': partnerp,
                                               'vat_no_p': vat_no_p, 
                                               'inv_date_p': inv_date_p,
                                               'inv_no_p': inv_nop,
                                               'P_base_total': format(round(abs(p_base_total_p), 2), ","), 
                                               'P_tax_total': format(round(abs(p_tax_total_p), 2), ","),
                                               'P_total': format(round(abs(p_total), 2), ","),
                                               'per_P': tax.amount})
            
            # print return bill and inv
            #print return inv
            mvr = self.env['account.move.line'].search(
                [('date', '>=', data['date_from']), ('date', '<=', data['date_to']),('tax_line_id', '=', tax.id)])
            if data['target_moves'] == 'all_posted':
                mvr = self.env['account.move.line'].search(
                    [('date', '>=', data['date_from']), ('date', '<=', data['date_to']), ('tax_line_id', '=', tax.id),
                     ('move_id.state','=','posted'),('move_id.name','=like','RINV%')])
            if mvr:
                for n in mvr:
                    if tax.type_tax_use == 'sale':
                        desc_r = n.name
                        partner_r = n.partner_id.name
                        vat_no_r = n.partner_id.vat
                        inv_date_r = n.date
                        inv_no_r = n.move_id.name
                        s_base_total_r = n.balance * 100 / tax.amount
                        s1_r += n.balance * 100 / tax.amount
                        s_tax_total_r = n.balance
                        s2_r += n.balance
                        s_total_r = (n.balance * 100 / tax.amount) + n.balance
                        s3_r += s_total_r
                        per_r= tax.amount
                        report_total_2.append({'desc_r': desc_r,
                                             'partner_r': partner_r,
                                             'vat_no_r': vat_no_r, 
                                             'inv_date_r': inv_date_r,
                                             'inv_no_r': inv_no_r,
                                             's_base_total_r': format(round(abs(s_base_total_r), 2), ","), 
                                             's_tax_total_r': format(round(abs(s_tax_total_r), 2), ","),
                                             's_total_r': format(round(abs(s_total_r), 2), ","),
                                             'per_r': per_r})
            # print return bill
            mvpr = self.env['account.move.line'].search(
                [('date', '>=', data['date_from']), ('date', '<=', data['date_to']),
                 ('tax_line_id', '=', tax.id)])
            if data['target_moves'] == 'all_posted':
                mvpr = self.env['account.move.line'].search(
                    [('date', '>=', data['date_from']), ('date', '<=', data['date_to']), ('tax_line_id', '=', tax.id),
                     ('move_id.state','=','posted'),('move_id.name','=like','RBILL%')])
            if mvpr:
                for n in mvpr:
                    if tax.type_tax_use == 'purchase':
                        desc_pr = n.name
                        partner_pr = n.partner_id.name
                        vat_no_pr = n.partner_id.vat
                        inv_date_pr = n.date
                        inv_no_pr = n.move_id.name
                        p_base_total_pr = n.balance * 100 / tax.amount
                        p1_pr += n.balance * 100 / tax.amount
                        p_tax_total_pr = n.balance
                        p2_pr += n.balance
                        p_total_pr = (n.balance * 100 / tax.amount) + n.balance
                        p3_pr += p_total_pr

                        report_total_4.append({'desc_pr': desc_pr,
                                             'partner_pr': partner_pr,
                                             'vat_no_pr': vat_no_pr, 
                                             'inv_date_pr': inv_date_pr,
                                             'inv_no_pr': inv_no_pr,
                                             'p_base_total_pr': format(round(abs(p_base_total_pr), 2), ","), 
                                             'p_tax_total_pr': format(round(abs(p_tax_total_pr), 2), ","),
                                             'p_total_pr': format(round(abs(p_total_pr), 2), ","),
                                             'per_pr': tax.amount})
        
        return {
            
            'report_total': report_total,
            'report_total_1': report_total_1,
            'report_total_2': report_total_2,
            'report_total_4': report_total_4,
            's1_r': format(round(abs(s1_r), 2), ","),
            's2_r': format(round(abs(s2_r), 2), ","),
            's3_r': format(round(abs(s3_r), 2), ","),
            's1': format(round(abs(s1), 2), ","),
            's2': format(round(abs(s2), 2), ","),
            's3': format(round(abs(s3), 2), ","),
            'p1': format(round(abs(p1), 2), ","),
            'p2': format(round(abs(p2), 2), ","),
            'p3': format(round(abs(p3), 2), ","),
            'p1_pr': format(round(abs(p1_pr), 2), ","),
            'p2_pr': format(round(abs(p2_pr), 2), ","),
            'p3_pr': format(round(abs(p3_pr), 2), ","),

            
            
        }



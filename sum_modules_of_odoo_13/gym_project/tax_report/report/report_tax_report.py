# -*- coding: utf-8 -*-
import time
import datetime
from odoo import api, models
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class ReporTaxReport(models.AbstractModel):
    _name = 'report.tax_report.action_report_tax_report'
    _description = "Tax Report"

    
    @api.model
    def _get_report_values(self, docids, data=None):
        if not data:
            raise UserError(_("Form content is missing, this report cannot be printed."))

        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('tax_report.action_report_tax_report')
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self,
            'date_from': data['date_from'],
            'date_to': data['date_to'],
            'data': data,
            'time': time,

            'report_total': data['report_total'],
            'report_total_1': data['report_total_1'],
            
            'tot': data['tot'],
            'sale': data['sale'],
            'purchase': data['purchase'],
         
            'sale_tot': data['sale_tot'],
            'purchase_tot': data['purchase_tot'],

            'ss_ref': data['ss_ref'],
            'ss_ref_tot': data['ss_ref_tot'],
            'pp_ref': data['pp_ref'],
            'pp_ref_tot': data['pp_ref_tot'],
        }

#CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCc
class ReporTaxReportDetailed(models.AbstractModel):
    _name = 'report.tax_report.action_report_tax_report_detailed'
    _description = "Tax Report"

    
    @api.model
    def _get_report_values(self, docids, data=None):
        if not data:
            raise UserError(_("Form content is missing, this report cannot be printed."))

        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('tax_report.action_report_tax_report_detailed')
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self,
            'date_from': data['date_from'],
            'date_to': data['date_to'],
            'data': data,
            'time': time,
            'report_total': data['report_total'],
            'report_total_1': data['report_total_1'],
            'report_total_2': data['report_total_2'],
            'report_total_4': data['report_total_4'],

            's1': data['s1'],
            's2': data['s2'],
            's3': data['s3'],
            's1_r': data['s1_r'],
            's2_r': data['s2_r'],
            's3_r': data['s3_r'],
            'p1': data['p1'],
            'p2': data['p2'],
            'p3': data['p3'],
            'p1_pr': data['p1_pr'],
            'p2_pr': data['p2_pr'],
            'p3_pr': data['p3_pr'],

        }

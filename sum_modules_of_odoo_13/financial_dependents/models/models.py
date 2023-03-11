
# from odoo import api, fields, models, _,tools
# from odoo.tools import float_compare, float_round, float_is_zero
# from odoo.exceptions import UserError
# import logging
# _logger = logging.getLogger(__name__)

# import psycopg2
# import pytz
# from itertools import groupby
# from itertools import zip_longest

# import json
# import re
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from datetime import date, timedelta
from itertools import groupby
from itertools import zip_longest
from hashlib import sha256
from json import dumps
from datetime import datetime, time
from pytz import timezone, UTC
from datetime import datetime, timedelta
# from .hijri_date import HijriDate
from babel.dates import format_datetime, format_date
import math
import calendar
from dateutil.relativedelta import relativedelta

import json
import re
class FinancialDependents(models.Model):
    _name = 'financial.dependents'
    _description = 'New Description'
    @api.model
    def _get_default_conf_dep_journal(self):
        param_obj = self.env['ir.config_parameter'].sudo()
        return int(param_obj.get_param('conf_dep_journal')) or False

    @api.model
    def _get_default_conf_dep_account_1(self):
        param_obj = self.env['ir.config_parameter'].sudo()
        return int(param_obj.get_param('conf_dep_account_1')) or False
    
    @api.model
    def _get_default_conf_cre_account_2(self):
        param_obj = self.env['ir.config_parameter'].sudo()
        return int(param_obj.get_param('conf_cre_account_2')) or False

    

    dep_journal_id = fields.Many2one('account.journal', string='Expence Account',default=_get_default_conf_dep_journal, readonly=True, domain="[('company_id', '=', company_id)]")
    sequence_id = fields.Char(string="Sequence",readonly=1)
    
    dep_amount = fields.Float(string='Amount')
    dep_date = fields.Date(string='Date')
    dep_memo  = fields.Char(string='Description')
   
    dep_dibet_account = fields.Many2one('account.account', string='Debit Account',readonly=1,default=_get_default_conf_dep_account_1,domain="[('company_id', '=', company_id)]")
    credit_cridet_account = fields.Many2one('account.account', string='Credit Account',readonly=1,default=_get_default_conf_cre_account_2,domain="[('company_id', '=', company_id)]")
    
    



    # @api.multi
	# def action_to(self):
	# 	if self.total_amounts == self.amount_total:
	# 		self.state = 'done'
	# 	else:
	# 		self.state = 'return'		
	# 	move_obj = self.env['account.move']
	# 	self.move_id = move_obj.create({
	# 		'ref':self.note,
	# 		'journal_id':self.journal_id.id,
	# 		'date': self.date,
	# 			})
	# 	self.env['account.move.line'].with_context(check_move_validity=False).create({
	# 		'name':"PettyCash",
	# 		'move_id':self.move_id.id,
    #         'account_id':self.account_id.id,
    #         'credit':self.total_amounts,
    #         'debit':0.0,
    #         'journal_id':self.journal_id.id,
    #         'date_maturity':self.date,
	# 		})
	# 	for rec in self:
	#  		for line in rec.Liquidation_ids:
	#  			self.env['account.move.line'].with_context(check_move_validity=False).create({
	#  				'move_id':self.move_id.id,
	# 		        'account_id':line.account_id.id,
	# 		        'credit':0.0,
	# 		        'debit':line.clear_amount,
	# 		        'state': 'posted',
	# 		        'journal_id':rec.journal_id.id,
	# 		        'date_maturity':rec.date
	# 		        })
    

    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='Status',default='draft')
    sequence = fields.Boolean(string='Sequence',default=True)
    config_tick = fields.Boolean(string='tick',default=True)

    @api.model
    def create(self,vals):
       
        seq = self.env['ir.sequence'].next_by_code('financial.dependents') or '/'
        vals['sequence_id'] = seq
        res = super(FinancialDependents,self).create(vals)
        return res
        
        
     
    
   





class ModuleName(models.Model):
    _name = 'liquidation.dependents'
    _description = 'New Description'

    name = fields.Char(string='Name')



class DependentsSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    def get_values(self):
        res = super(DependentsSettings, self).get_values()
        param_obj_dep = self.env['ir.config_parameter'].sudo()
        res.update(
	        conf_dep_journal = int(param_obj_dep.get_param('conf_dep_journal',default='0')) , 
            conf_dep_account_1 = int(param_obj_dep.get_param('conf_dep_account_1',default='0')),
            conf_cre_account_2 = int(param_obj_dep.get_param('conf_cre_account_2',default='0'))      
	    )
        return res
    
    def set_values(self):
        res = super(DependentsSettings, self).set_values()
        param_obj_dep = self.env['ir.config_parameter'].sudo()
        param_obj_dep.set_param('conf_dep_journal', self.conf_dep_journal and self.conf_dep_journal.id or False)
        param_obj_dep.set_param('conf_dep_account_1', self.conf_dep_account_1 and self.conf_dep_account_1.id or False)
        param_obj_dep.set_param('conf_cre_account_2', self.conf_cre_account_2 and self.conf_cre_account_2.id or False)
        return res


    conf_dep_journal = fields.Many2one('account.journal', string='Defuelt journal')
    
    conf_dep_account_1 = fields.Many2one('account.account', string='Defuelt Debit Account')
    conf_cre_account_2 = fields.Many2one('account.account', string='Defuelt Credit Account')
    
    

    @api.model
    def get_default_name(self):
        mado = self.conf_dep_journal
        return mado
   


   
   




     
    
     







    
    

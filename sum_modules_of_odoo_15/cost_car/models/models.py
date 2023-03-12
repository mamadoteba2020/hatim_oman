# -*- coding: utf-8 -*-


from odoo import api, fields, models, _

# class CarCar(models.Model):
#     _name = 'car.car'
#     _description = 'New Description'

#     name = fields.Char(string='Name')


# class SaleOrderCustom(models.Model):
#     _inherit = 'stock.picking'
#     car_id = fields.Many2one(comodel_name='car.car', string='Number Car')
#     analytic_cus = fields.Many2one(comodel_name='account.analytic', string='Analitic Account')
    
    




class StockPickinganalyticAccount(models.Model):
    _inherit = "stock.picking"
    analytic_account_id = fields.Many2one('account.analytic.account','Analytic Account')
    

    # def button_validate(self):
    #     """ On SO confirmation, analytic account will be created automatically. """
    #     result = super(StockPickinganalyticAccount, self).button_validate()
        # if the SO not already linked to analytic account, create a new analytic account and set to so analytic account.
        # obj_move_line = self.env['account.move.line']
        # obj_move_line.with_context(check_move_validity = False).create({
        #     'analytic_account_id':self.analytic_account_id.id,})
    #     if not self.analytic_account_id:
    #         self._analytic_picking_account_generation()
    #     return result

    # def _stockpicking_create_analytic_account_prepare_values(self):
    #     """
    #      Prepare values to create analytic account
    #     :return: list of values
    #     """
    #     return {
    #         'name': '%s' % self.name,
    #         'partner_id': self.partner_id.id,
    #         'company_id': self.company_id.id,
    #     }


    # def _analytic_picking_account_generation(self):
    #     """ Generate analytic account for the so , and link it.
    #         :return a mapping with the so id and its linked analytic account
    #         :rtype dict
    #     """
    #     result = {}
    #     values = self._stockpicking_create_analytic_account_prepare_values()
    #     analytic_account = self.env['account.analytic.account'].sudo().create(values)
    #     self.write({'analytic_account_id': analytic_account.id})
    #     result[self.id] = analytic_account
    #     return result





    #   move_obj = self.env['account.move']
    #     move_id = move_obj.create({

    #         'ref':self.sequence_id,
    #         'journal_id':self.dep_journal_id.id,
    #         'date': self.dep_date,})
    #     obj_move_line = self.env['account.move.line']
    #     obj_move_line.with_context(check_move_validity = False).create({
    #         'name':'PettyCash',
    #         'move_id':move_id.id,
    #         'account_id':self.credit_cridet_account.id,
    #         'credit':self.dep_amount,
    #         'debit':0.0,
    #         'journal_id':self.dep_journal_id.id,
    #         'partner_id':self.emp_partner_id.id,
    #         'date_maturity':self.dep_date,})

    #     obj_move_line.with_context(check_move_validity = False).create({
    #         'name':'PettyCash',
    #         'move_id':move_id.id,
    #         'account_id':self.dep_dibet_account.id,
    #         'credit':0.0,
    #         'debit':self.dep_amount,
    #         'journal_id':self.dep_journal_id.id,
    #         'partner_id':self.emp_partner_id.id,
    #         'date_maturity':self.dep_date,})
        
    #     liquidation_obj = self.env['liquidation.dependents']
    #     liquidation_id = liquidation_obj.create({
    #         'liq_journal_id':self.dep_journal_id.id,
    #         'dep_liq_sequence_id':self.sequence_id,
    #         'dep_amount_liq': self.dep_amount,
    #         'dep_date_liq': self.dep_date,
    #         'credit_liq_account': self.dep_dibet_account.id,
    #         # 'sequence_liquidation':,
    #         'liq_partner_id': self.emp_partner_id.id,})
    #     self.state = 'done'









class StockMoveCustom(models.Model):
    _inherit = 'stock.move'

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description):
        # This method returns a dictionary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
        self.ensure_one()
        debit_line_vals = {
            'name': description,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': description,
            'partner_id': partner_id,
            'debit': debit_value if debit_value > 0 else 0,
            'credit': -debit_value if debit_value < 0 else 0,
            'account_id': debit_account_id,
            'analytic_account_id': self.picking_id.analytic_account_id.id,
        }

        credit_line_vals = {
            'name': description,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': description,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': credit_account_id,
        }

        rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}
        if credit_value != debit_value:
            # for supplier returns of product in average costing method, in anglo saxon mode
            diff_amount = debit_value - credit_value
            price_diff_account = self.product_id.property_account_creditor_price_difference

            if not price_diff_account:
                price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
            if not price_diff_account:
                raise UserError(_('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

            rslt['price_diff_line_vals'] = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': description,
                'partner_id': partner_id,
                'credit': diff_amount > 0 and diff_amount or 0,
                'debit': diff_amount < 0 and -diff_amount or 0,
                'account_id': price_diff_account.id,
            }
        return rslt
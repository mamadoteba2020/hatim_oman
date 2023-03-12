# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,_
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.tools.misc import format_date

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    invoice_count = fields.Integer(string='Credit Note', compute='_compute_invoice_count')
    has_credit_note = fields.Boolean()
    credit_invoice_id = fields.Many2one('account.move')
    credit_note_order_bol = fields.Boolean(string="credit_note_order_bol", default=False)

    def _compute_invoice_count(self):
        """
        @desc: For count the credit note which are created from return delivery order.
        """
        for picking in self:
            move_ids = picking.env['account.move'].search([('invoice_origin', '=', picking.name)])
            self.invoice_count = move_ids and len(move_ids) or 0

    def action_see_credit_note(self):
        return {
            'name': _('Credit Note'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id', '=', self.credit_invoice_id.id)],
        }

    # def action_open_picking_invoice(self):
    #     """
    #     @desc: For redirect to the credit note related to the current picking.
    #     @return: Action for latest created credit note.
    #     """
    #     return {
    #         'name': 'Invoices',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'tree,form',
    #         'res_model': 'account.move',
    #         'domain': [('invoice_origin', '=', self.name)],
    #         'context': {'create': False},
    #         'target': 'current'
    #     }

    def button_validate_credit(self):
        # Clean-up the context key at validation to avoid forcing the creation of immediate
        # transfers.
        ctx = dict(self.env.context)
        ctx.pop('default_immediate_transfer', None)
        self = self.with_context(ctx)

        # Sanity checks.
        pickings_without_moves = self.browse()
        pickings_without_quantities = self.browse()
        pickings_without_lots = self.browse()
        products_without_lots = self.env['product.product']
        for picking in self:
            if not picking.move_lines and not picking.move_line_ids:
                pickings_without_moves |= picking

            picking.message_subscribe([self.env.user.partner_id.id])
            picking_type = picking.picking_type_id
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
            no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in picking.move_line_ids)
            if no_reserved_quantities and no_quantities_done:
                pickings_without_quantities |= picking

            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = picking.move_line_ids
                if not no_quantities_done:
                    lines_to_check = lines_to_check.filtered(lambda line: float_compare(line.qty_done, 0, precision_rounding=line.product_uom_id.rounding))
                for line in lines_to_check:
                    product = line.product_id
                    if product and product.tracking != 'none':
                        if not line.lot_name and not line.lot_id:
                            pickings_without_lots |= picking
                            products_without_lots |= product

        if not self._should_show_transfers():
            if pickings_without_moves:
                raise UserError(_('Please add some items to move.'))
            if pickings_without_quantities:
                raise UserError(self._get_without_quantities_error_message())
            if pickings_without_lots:
                raise UserError(_('You need to supply a Lot/Serial number for products %s.') % ', '.join(products_without_lots.mapped('display_name')))
        else:
            message = ""
            if pickings_without_moves:
                message += _('Transfers %s: Please add some items to move.') % ', '.join(pickings_without_moves.mapped('name'))
            if pickings_without_quantities:
                message += _('\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved nor done. To force these transfers, switch in edit more and encode the done quantities.') % ', '.join(pickings_without_quantities.mapped('name'))
            if pickings_without_lots:
                message += _('\n\nTransfers %s: You need to supply a Lot/Serial number for products %s.') % (', '.join(pickings_without_lots.mapped('name')), ', '.join(products_without_lots.mapped('display_name')))
            if message:
                raise UserError(message.lstrip())

        # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
        # moves and/or the context and never call `_action_done`.
        if not self.env.context.get('button_validate_picking_ids'):
            self = self.with_context(button_validate_picking_ids=self.ids)
        res = self._pre_action_done_hook()
        if res is not True:
            return res

        # Call `_action_done`.
        if self.env.context.get('picking_ids_not_to_backorder'):
            pickings_not_to_backorder = self.browse(self.env.context['picking_ids_not_to_backorder'])
            pickings_to_backorder = self - pickings_not_to_backorder
        else:
            pickings_not_to_backorder = self.env['stock.picking']
            pickings_to_backorder = self
        pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
        pickings_to_backorder.with_context(cancel_backorder=False)._action_done()

        if self.user_has_groups('stock.group_reception_report') \
                and self.user_has_groups('stock.group_auto_reception_report') \
                and self.filtered(lambda p: p.picking_type_id.code != 'outgoing'):
            lines = self.move_lines.filtered(lambda m: m.product_id.type == 'product' and m.state != 'cancel' and m.quantity_done and not m.move_dest_ids)
            if lines:
                # don't show reception report if all already assigned/nothing to assign
                wh_location_ids = self.env['stock.location']._search([('id', 'child_of', self.picking_type_id.warehouse_id.view_location_id.id), ('usage', '!=', 'supplier')])
                if self.env['stock.move'].search([
                        ('state', 'in', ['confirmed', 'partially_available', 'waiting', 'assigned']),
                        ('product_qty', '>', 0),
                        ('location_id', 'in', wh_location_ids),
                        ('move_orig_ids', '=', False),
                        ('picking_id', 'not in', self.ids),
                        ('product_id', 'in', lines.product_id.ids)], limit=1):
                    action = self.action_view_reception_report()
                    action['context'] = {'default_picking_ids': self.ids}
                    return action
   
        for rec in self:
            invoice_ids = []
            if rec.sale_id:
                if not rec.sale_id.invoice_ids.ids:
                    raise UserError(
                        _("Invoice is not generated for this order Please \
                        Create Invoice"))
                for invoice in rec.sale_id.invoice_ids:
                    if invoice.move_type == 'out_invoice' and \
                            invoice.state in ['draft', 'cancel']:
                        raise UserError(
                            _("It looks like one of invoice is canceled \
                            not validate."))
                    invoice_ids.append(invoice)
                invoice = self.env['account.move'].create({
                    'partner_id': rec.partner_id.id,
                    'move_type': 'out_refund',
                    'fiscal_position_id': rec.partner_id.property_account_position_id.id,
                    'invoice_date': fields.Date.context_today(rec),
                    'invoice_origin': rec.sale_id.name
                })
                for line in rec.move_lines:
                    line_values = {
                        'product_id': line.product_id.id,
                        'move_id': invoice.id,
                        'currency_id': line.company_id.currency_id.id,
                        'quantity': line.product_uom_qty
                    }
                    # create a record in cache, apply onchange then revert back
                    # to a dictionnary
                    invoice_line = self.env['account.move.line'].new(
                        line_values)
                    invoice_line._onchange_product_id()
                    line_values = invoice_line._convert_to_write(
                        {name: invoice_line[name] for name in invoice_line._cache})
                    line_values['tax_ids'] = False
                    if invoice_ids:
                        for inv in invoice_ids:
                            for l in inv.invoice_line_ids:
                                if not line_values['tax_ids']:
                                    if l.product_id.id == line.product_id.id and l.tax_ids:
                                        line_values['tax_ids'] = [
                                            (6, 0, l.tax_ids.ids)]
                    invoice.write({'invoice_line_ids': [(0, 0, line_values)]})
                invoice_line._get_computed_taxes()
                xml_id = invoice.move_type == 'out_invoice' and 'action_move_out_invoice_type' or \
                    invoice.move_type == 'out_refund' and 'action_move_out_refund_type' or \
                    invoice.move_type == 'in_invoice' and 'action_move_in_invoice_type' or \
                    invoice.move_type == 'in_refund' and 'action_move_in_refund_type'
                # Put the reason in the chatter
                subject = _("Invoice refund")
                body = 'Invoice Refund'
                invoice.message_post(body=body, subject=subject)
                self.has_credit_note = True
                self.credit_invoice_id = invoice.id
                if xml_id:
                    result = self.env.ref('account.%s' % (xml_id)).read()[0]
                    result['domain'] = [
                        ('move_type', '=', 'out_refund'), ('id', '=', invoice.id)]
                    return result
                return True
        return True
    

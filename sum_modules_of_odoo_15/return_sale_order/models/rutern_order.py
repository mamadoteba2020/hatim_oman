from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrderReturn(models.Model):
    _name = 'sale.order.return'
    _description = "Returns for sale order"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    @api.model
    def default_get(self, fields_list):
        res = super(SaleOrderReturn, self).default_get(fields_list)
        partner = self.env['res.partner'].browse(res.get('partner_id'))
        addr = partner.address_get(['delivery', 'invoice'])
        res['partner_invoice_id'] = addr['invoice']
        res['partner_shipping_id'] = addr['delivery']
        return res

    name = fields.Char(string='Return Order',
                       required=True,
                       copy=False,
                       readonly=True,
                       default=lambda self: _('New'))
    # S_O_rel = fields.Char(string='Return Order',required=True)
    partner_id = fields.Many2one('res.partner', string="Customer")
    date_of_return = fields.Datetime(string="Return Date", default=datetime.today())
    group_id_return_order = fields.Many2one("procurement.group")
    my_sale_order_id = fields.Many2one('sale.order', string="Return of", required=True,
                                        domain="[('partner_id', '=', partner_id)]")
    my_sale_order_return_line_ids = fields.One2many('sale.order.return.line',
                                                     'my_sale_return_id',)
    note = fields.Text()
    partner_invoice_id = fields.Many2one(
        'res.partner', string='Invoice Address',)
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Delivery Address')
    user_id = fields.Many2one(
        'res.users', string='Salesperson',
        default=lambda self: self.env.user,)
    company_id = fields.Many2one(
        'res.company', 'Company',
        required=True, index=True, default=lambda self: self.env.company)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Return Order')], default='draft',
                             track_visibility="always")
    my_picking_ids = fields.Many2many('stock.picking', 'return_order_picking_rel',
                                       'return_id', 'stock_pick_id',
                                       string='Returns',
                                       copy=False, store=True)
    incoming_count = fields.Integer(string="Incoming shipments",
                                    compute="_compute_picks")

    @api.depends('my_picking_ids')
    def _compute_picks(self):
        for rec in self:
            rec.incoming_count = 0
            if rec.my_picking_ids:
                rec.incoming_count = len(rec.my_picking_ids.ids)

    @api.model
    def create(self, vals):
        if(vals.get('name', _('New')) == _('New')):
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.order.return')
        return super(SaleOrderReturn, self).create(vals)

    @api.onchange('partner_id')
    def _reset_sale_details(self):
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
            })
            return
        addr = self.partner_id.address_get(['delivery', 'invoice'])
        self = self.with_company(self.company_id)

        values = {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'my_sale_order_id':''
        }
        partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
        user_id = partner_user.id
        if not self.env.context.get('not_self_saleperson'):
            user_id = user_id or self.env.uid
        if user_id and self.user_id.id != user_id:
            values['user_id'] = user_id

        
        self.update(values)

    @api.onchange('my_sale_order_id')
    def _get_sales_details(self):
        if not self.my_sale_order_id:
            self.update({
                    'user_id': False,
                    'team_id': False,
                    'company_id': False
                })
            return
        if self.my_sale_order_id:
            values = {
                'user_id': self.my_sale_order_id.user_id,
                'team_id': self.my_sale_order_id.team_id,
                'company_id':self.my_sale_order_id.company_id
            }
        self.update(values)
        
    def action_view_in_picking(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        pickings = self.mapped('my_picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [
                    (state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        return action

    def button_confirm_two2(self):
        picking_type_id = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming'),
             ('company_id', '=', self.company_id.id)], limit=1)
        if picking_type_id:
            res = self._prepare_picking(self, picking_type_id)
            new_picking_id = self.env['stock.picking'].create(res)
            self.my_sale_order_id.my_picking_ids = [(4, new_picking_id.id, 0)]
            self.my_picking_ids = [(4, new_picking_id.id, 0)]
            for line in self.my_sale_order_return_line_ids:
                move_vals = self._prepare_stock_moves(
                    self, line, picking_type_id, new_picking_id)
                for move_val in move_vals:
                    self.env['stock.move'].create(move_val)._action_confirm()._action_assign()
                self.env.cr.commit()
            self.process(new_picking_id)
            return_picking = []
            if self.env.context.get('active_id') and self.env.context.get('active_model') == 'stock.picking':
                act1 =self.env.context.get('active_id')
                print(act1)
                return_picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
                for wizard in return_picking:
                    new_picking_id, pick_type_id = wizard._create_returns()
        
                picking_id = new_picking_id and self.env['stock.picking'].browse(new_picking_id) or None
                moves = picking_id and picking_id.sale_id and self.env['account.move'].browse(
                picking_id.sale_id.invoice_ids.ids)
                current_user = picking_id.env.uid

                invoice_line_list = []
                for move_ids_without_package in picking_id.move_lines:
                    vals = (0, 0, {
                        'name': move_ids_without_package.description_picking,
                        'product_id': move_ids_without_package.product_id.id,
                        'price_unit': move_ids_without_package.product_id.lst_price,
                        'account_id': move_ids_without_package.product_id.property_account_income_id.id if move_ids_without_package.product_id.property_account_income_id
                        else move_ids_without_package.product_id.categ_id.property_account_income_categ_id.id,
                        'tax_ids': [(6, 0, [picking_id.company_id.account_sale_tax_id.id])],
                        'quantity': move_ids_without_package.product_uom_qty,
                    })
                invoice_line_list.append(vals)
                self.env['account.move'].create({
                'move_type': 'out_refund',
                'invoice_origin': picking_id.name,
                'invoice_user_id': current_user,
                'narration': picking_id.name,
                'partner_id': picking_id.partner_id.id,
                'currency_id': picking_id.env.user.company_id.currency_id.id,
                'ref': _('Reversal for: %s') % self.reason if self.reason else '',
                'date': self.date or False,
                'invoice_date': self.date or False,
                'journal_id': self.journal_id and self.journal_id.id or moves[0].journal_id.id,
                'invoice_line_ids': invoice_line_list
                })
                #  
                ctx = dict(self.env.context)
                ctx.update({
                'default_partner_id': self. my_picking_ids.partner_id.id,
                'search_default_picking_type_id': pick_type_id,
                'search_default_draft': False,
                'search_default_assigned': False,
                'search_default_confirmed': False,
                'search_default_ready': False,
                'search_default_late': False,
                'search_default_available': False,
                })
                return {
                    'name': _('Returned Picking'),
                    'view_mode': 'form,tree,calendar',
                    'res_model': 'stock.picking',
                    'res_id': new_picking_id,
                    'type': 'ir.actions.act_window',
                    'context': ctx,
                }
            self.state = 'confirm'
            try:
                res = new_picking_id.button_validate()
                if res:
                    if res.get('res_model') == 'stock.immediate.transfer':
                        wizard = self.env['stock.immediate.transfer'].browse(
                            res.get('res_id'))
                        wizard.process()
                        return True
                return res
            except Exception:
                pass
        return True



    def button_confirm(self):
        picking_type_id = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming'),
             ('company_id', '=', self.company_id.id)], limit=1)
        if picking_type_id:
            res = self._prepare_picking(self, picking_type_id)
            new_picking_id = self.env['stock.picking'].create(res)
            self.my_sale_order_id.my_picking_ids = [(4, new_picking_id.id, 0)]
            self.my_picking_ids = [(4, new_picking_id.id, 0)]
            for line in self.my_sale_order_return_line_ids:
                move_vals = self._prepare_stock_moves(
                    self, line, picking_type_id, new_picking_id)
                for move_val in move_vals:
                    self.env['stock.move'].create(move_val)._action_confirm()._action_assign()
                self.env.cr.commit()
            self.process(new_picking_id)
            self.state = 'confirm'
            # button_validate()
            try:
                #when want ready replace button_validate() with action_confirm()
                res = new_picking_id.action_confirm()
                if res:
                    if res.get('res_model') == 'stock.immediate.transfer':
                        wizard = self.env['stock.immediate.transfer'].browse(
                            res.get('res_id'))
                        wizard.process()
                        return True
                return res
            except Exception:
                pass
        return True

    def button_account_move_confirm(self):
        # picking_type_two = self.env['stock.picking.type'].search(
        #     [('code', '=', 'incoming'),
        #      ('company_id', '=', self.company_id.id)], limit=1)
        # print('this is ', picking_type_two)
        return_picking = None
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'stock.picking':
            act1 =self.env.context.get('active_id')
            print(act1)
            return_picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))

        # Create reverse stock moves (Return Delivery Order)  
        
        # for wizard in return_picking:
        #     pick_type_id = wizard._create_returns()
    
        # Create reverse account moves (Credit Note)
        picking_id = new_picking_id and self.env['stock.picking'].browse(new_picking_id) or None
        moves = picking_id and picking_id.sale_id and self.env['account.move'].browse(
            picking_id.sale_id.invoice_ids.ids)
        current_user = picking_id.env.uid

        invoice_line_list = []
        for move_ids_without_package in picking_id.move_lines:
            vals = (0, 0, {
                'name': move_ids_without_package.description_picking,
                'product_id': move_ids_without_package.product_id.id,
                'price_unit': move_ids_without_package.product_id.lst_price,
                'account_id': move_ids_without_package.product_id.property_account_income_id.id if move_ids_without_package.product_id.property_account_income_id
                else move_ids_without_package.product_id.categ_id.property_account_income_categ_id.id,
                'tax_ids': [(6, 0, [picking_id.company_id.account_sale_tax_id.id])],
                'quantity': move_ids_without_package.product_uom_qty,
            })
            invoice_line_list.append(vals)
        self.env['account.move'].create({
            'move_type': 'out_refund',
            'invoice_origin': picking_id.name,
            'invoice_user_id': current_user,
            'narration': picking_id.name,
            'partner_id': picking_id.partner_id.id,
            'currency_id': picking_id.env.user.company_id.currency_id.id,
            'ref': _('Reversal for: %s') % self.reason if self.reason else '',
            'date': self.date or False,
            'invoice_date': self.date or False,
            'journal_id': self.journal_id and self.journal_id.id or moves[0].journal_id.id,
            'invoice_line_ids': invoice_line_list
        })

        ctx = dict(self.env.context)
        ctx.update({
            'default_partner_id': self.picking_id.partner_id.id,
            'search_default_picking_type_id': pick_type_id,
            'search_default_draft': False,
            'search_default_assigned': False,
            'search_default_confirmed': False,
            'search_default_ready': False,
            'search_default_late': False,
            'search_default_available': False,
        })
        return {
            'name': _('Returned Picking'),
            'view_mode': 'form,tree,calendar',
            'res_model': 'stock.picking',
            'res_id': new_picking_id,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }



    def _prepare_picking(self, move, picking_type_id):
        
        partner = self.my_sale_order_id.partner_id
        sorel = self.my_sale_order_id.name
        # group_rel_so = self.knk_sale_order_id.procurement_group_id.id
        # print("this is " ,group_rel_so)
        # move_value_return = self.knk_sale_order_id.order_line.move_ids.group_id.id
        # print("this is move" ,move_value_return)
        location_id = partner.property_stock_customer.id
        location_dest_id = picking_type_id.default_location_dest_id.id
        valeu_true=True
        return {
            'picking_type_id': picking_type_id.id,
            'partner_id': partner.id,
            'date': self.date_of_return,
            'origin':'RETURN OF SALE ORDER'+'  '+'('+sorel+')',
            'credit_note_order_bol': True,
            'location_dest_id': location_dest_id,
            'location_id': location_id,
            'company_id': self.my_sale_order_id.company_id.id,
            'move_type': 'direct'
        }

    def _prepare_stock_moves(self, move, line, picking_type_id, picking):
        res = []
        partner = self.my_sale_order_id.partner_id
        location_id = partner.property_stock_customer.id
        location_dest_id = picking_type_id.default_location_dest_id.id
        id_group = self.my_sale_order_id.procurement_group_id.id
        template = {
            'name': line.my_product_id.name,
            'product_id': line.my_product_id.id,
            'product_uom': line.my_product_id.uom_id.id,
            'product_uom_qty': line.my_product_qty,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'group_id':id_group,
            'picking_id': picking.id,
            'partner_id': partner.id,
            'state': 'draft',
            'company_id': self.my_sale_order_id.company_id.id,
            'picking_type_id': picking_type_id.id,
            'route_ids': picking_type_id.warehouse_id and [
                (6, 0, [
                    x.id for x in picking_type_id.warehouse_id.route_ids])] or
            [],
            'warehouse_id': picking_type_id.warehouse_id.id,
        }
        res.append(template)
        return res

    def process(self, picking):
        pickings_to_validate = self.env['stock.picking']
        # If still in draft => confirm and assign
        if picking.state == 'draft':
            picking.action_confirm()
            if picking.state != 'assigned':
                picking.action_assign()
                if picking.state != 'assigned':
                    raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
        for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
            for move_line in move.move_line_ids:
                move_line.qty_done = move_line.product_uom_qty
        return pickings_to_validate.with_context(skip_immediate=True).button_validate()



class SaleOrderReturnLine(models.Model):
    _name = 'sale.order.return.line'
    _description = "Returns lines for sale order"

    my_sale_return_id = fields.Many2one('sale.order.return')
    my_product_id = fields.Many2one('product.product',
                                     string="Product",
                                     required="True")
    my_product_qty = fields.Float(string="Quantity")
    reason_to_return = fields.Char(string="Reason")


    @api.onchange('my_sale_return_id')
    def _domain_change(self):
        domain = []
        for line in self.my_sale_return_id.my_sale_order_id.order_line:
            if line.qty_delivered > 0:
                domain.append(line.product_id.id)
        return {
            'domain': {
                'my_product_id': [('id', 'in', domain)]}
        }

    @api.constrains('my_product_qty')
    def check_quantity(self):
        for rec in self:
            lines = rec.my_sale_return_id.\
                my_sale_order_id.order_line.filtered(
                    lambda x: x.product_id == rec.my_product_id)
            for line in lines:
                if(rec.my_product_qty > line.my_balanced_qty):
                    raise UserError(
                        'Return quantity cannot be more than Delivered Quantity')
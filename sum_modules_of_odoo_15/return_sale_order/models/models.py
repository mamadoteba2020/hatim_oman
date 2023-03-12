

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    my_sale_return_show = fields.Boolean(compute="_check_sale_return_show")
   
    my_picking_ids = fields.Many2many('stock.picking', 'return_picking_rel',
                                       'sale_id', 'stock_pick_id',
                                       string='Returns',
                                       copy=False, store=True)
    incoming_count = fields.Integer(string="Incoming shipments",
                                    compute="_compute_picks")
 
    my_return_ids = fields.One2many('sale.order.return', 'my_sale_order_id',
                                     string="Returns", readonly=True)
    procurement_group_id = fields.Many2one('procurement.group', 'Procurement Group', copy=True)
    # my_return_ids = fields.One2many('create.return.sale', 'knk_sale_order_id',
    #                                  string="Returns", readonly=True)

    @api.depends('my_picking_ids')
    def _compute_picks(self):
        for rec in self:
            rec.incoming_count = 0
            if rec.my_picking_ids:
                rec.incoming_count = len(rec.my_picking_ids)

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

    @api.depends('picking_ids')
    def _check_sale_return_show(self):
        for rec in self:
            rec.my_sale_return_show = False
            picks = rec.picking_ids.filtered(lambda x: x.picking_type_code == 'outgoing' and x.state == 'done')
            if picks:
                rec.my_sale_return_show = True

    def open_sale_return(self):
        ctx = self.env.context.copy()
        ctx.update({
            'default_my_sale_order_id': self.id,
        })
        return{
            'name': 'Returns',
            'type': 'ir.actions.act_window',
            'res_model': 'create.return.sale',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx
        }







class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"

   
    my_return_qty = fields.Float(string="Returned",
                                  compute="_return_qty_count")
    my_balanced_qty = fields.Float(string="Balanced", compute="_return_qty_count")

    @api.depends('order_id.my_picking_ids')
    def _return_qty_count(self):
        for rec in self:
            picks = self.env['stock.picking'].search(
                [('id', 'in', rec.order_id.my_picking_ids.ids),
                 ('state', '=', 'done')])
            qty = 0
            for pick in picks:
                line = pick.move_ids_without_package.filtered(
                    lambda x: x.product_id == rec.product_id)
                qty += line.quantity_done
            rec.my_return_qty = qty
            rec.my_balanced_qty = rec.qty_delivered - rec.my_return_qty



    






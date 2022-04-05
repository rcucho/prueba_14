from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class SaleOrderLine2Component(models.Model):
    _inherit = 'sale.order.line'
    
    custom_product = fields.Boolean(related="product_template_id.customizable", string="Producto Personalizable")
    #-------------------------------------------------------------------------------------------------------------------------------------
    change_component = fields.One2many('change.component', 'change_order_line', string="Cambio de componentes")
    product_bom = fields.Many2one('mrp.bom', string="Lista de Materiales", compute='_compute_product_bom')
     
    @api.onchange('product_id')
    def _compute_product_bom(self):
        for rec in self:
            if rec.product_id:
                rec.product_bom = rec.product_id.bom_ids[0].id
    
    def action_show_details(self):
        self.ensure_one()
        view = self.env.ref('mstech_components.sale_order_line_view_form_component')

        return {
            'name': _('Detailed Order Line'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': {},
        }
            
    @api.onchange('discount')
    def compute_amount_discount_margin(self):
        for line in self:
            mount_disc = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            margin=[]
            if line.change_component:
                for change in line.change_component:
                    margin_x = change.product_in.lst_price - change.product_in.standard_price
                    margin.append(margin_x)  
                if mount_disc > min(margin):
                    raise UserError("El monto del descuento no pueder ser menor al margen entre el costo y precio de uno de los componente entrante")
   
    @api.onchange('change_component')
    def compute_customer_lead(self):
        for line in self:
            cust_le = line.product_id.sale_delay
            if line.change_component:
                for change in line.change_component:
                    cust_le = cust_le - change.product_out.sale_delay + change.product_in.sale_delay
            line.customer_lead = cust_le
            
            if line.customer_lead < 0:
                raise UserError("La fecha de entrega al cliente no puede ser menor a cero.")
    
    @api.onchange('change_component')
    def compute_price_unit(self):
        for line in self:
            price_s = line.product_id.lst_price
            if line.change_component:
                for change in line.change_component:
                    price_s = price_s - change.product_out.lst_price + change.product_in.lst_price
            line.price_unit = price_s
            
            if line.price_unit < line.product_id.standard_price:
                raise UserError("El precio del producto no puede ser menor al costo del mismo. Necesita reformular los componentes")      
                            
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def action_confirm(self):
        result = super().action_confirm()
        for rec in self:
            if rec.state == 'sale' and rec.mrp_production_count > 0: 
                for line_order in rec.order_line:
                    mrp_order2 = self.env['mrp.production'].search([('origin','=',rec.name),('product_id','=',line_order.product_id.id)])
                    list_in = line_order.change_component.mapped('product_in.id')
                    for change in line_order.change_component:
                        for line in mrp_order2.move_raw_ids:
                            if line.product_id.id == change.product_out.id:
                                qnty = line.product_uom_qty
                                line.write({'state':'draft'})
                                line.unlink()
                                mrp_order2.move_raw_ids.create(mrp_order2._get_move_raw_values(change.product_in, qnty,line_order.product_uom))
                                mrp_order2.move_byproduct_ids.create(mrp_order2._get_move_finished_values(change.product_out.id, qnty,line_order.product_uom.id))
                    for line2 in mrp_order2.move_raw_ids:
                        if not line2.product_id.id in list_in:
                            line2.write({'state':'draft'})
                            line2.unlink()
                    mrp_order2.move_raw_ids.create(mrp_order2._get_move_raw_values(line_order.product_id, 1.0,line_order.product_uom))
                    
        return result

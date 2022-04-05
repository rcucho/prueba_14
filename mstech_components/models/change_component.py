from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ChangeComponent(models.Model):
    _name = 'change.component'
    _description = "Created for change Components"
    
    name = fields.Char(string='Nombre')
    change_order_line = fields.Many2one('sale.order.line', string="Linea de Orden de Venta")
    product_out = fields.Many2one('product.product', string="Productos Salientes", domain="[('bom_line_ids', '!=', False)]") #domain="[('customizable', '=', True)]")
                                                                                          
    product_in = fields.Many2one('product.product', string="Productos Entrantes")
    
    bom_order_line = fields.Many2one('mrp.bom', related='change_order_line.product_bom',string=" BOM Linea de Orden de Venta")
    
    #@api.onchange('change_order_line')
    #def _compute_component_out(self):
        #for rec in self:
            #bom = rec.change_order_line.product_bom
            #parts = bom.bom_line_ids.mapped('product_id')
            #if bom:
                #raise UserError(str(parts)+str(rec.bom_order_line))
                
            

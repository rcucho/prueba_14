from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    customizable = fields.Boolean(string='Personalizable?')
    
class ProductProduct(models.Model):
    _inherit = 'product.product'

    sol_component_out = fields.Many2one('sale.order.line', string="Componente Sale in SOL")
    sol_component_in = fields.Many2one('sale.order.line', string="Componente Entra in SOL")

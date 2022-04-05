from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    mrp_mipclista = fields.Boolean(string="Fabricacion natural", default=False, compute='_onchange_mrp_mipclista') 
    
    #@api.depends('state')
    #def _compute_mrp_mipclista(self):
        #for rec in self:
            #rec._onchange_mrp_mipclista()
    
    @api.onchange('state')
    def _onchange_mrp_mipclista(self):
        for rec in self:
            var = 0
            for move in rec.move_raw_ids:
                if rec.product_id == move.product_id:
                   var = var + 1 
                    #rec.mrp_mipclista = True
                else:
                    var = var + 0
            if var > 0:
                rec.mrp_mipclista = True
            else:
                rec.mrp_mipclista = False
    
    def _check_sn_uniqueness(self):
        for rec in self:
            condition_sn = False
            if rec.product_tracking == 'serial' and rec.lot_producing_id:
                if rec._is_finished_sn_already_produced(rec.lot_producing_id):
                    if rec.mrp_mipclista :
                        condition_sn = True
            if not condition_sn:
                super()._check_sn_uniqueness()
    
    @api.constrains('product_id', 'move_raw_ids')
    def _check_production_lines(self):
        for production in self:
            condition = False
            for move in production.move_raw_ids:
                if production.product_id == move.product_id:# and move.lot_ids:
                    condition = True
            if not condition:
                #super()._check_production_lines()
                pass
            
    @api.onchange('move_raw_ids.lot_ids')
    def onchange_lot_producing(self):
        for production in self:
            for move in production.move_raw_ids:
                if production.product_id == move.product_id:
                    production.lot_producing_id = move.lot_ids[0].id
    
    def action_generate_serial(self):
        for production in self:
            for move in production.move_raw_ids:
                if production.product_id == move.product_id:
                    raise UserError("No puedes generar un nuevo lote teniendo el mismo producto como componente.")
            super().action_generate_serial()

# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductAttributeValue(models.Model):

    _inherit = "product.attribute.value"

    product_attr_group_id = fields.Many2many(
        comodel_name="product.attribute.group", string="Attribute Group"
    )

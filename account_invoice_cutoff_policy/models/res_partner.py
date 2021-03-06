# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from dateutil.rrule import rrule, DAILY
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ResPartner(models.Model):

    _inherit = "res.partner"

    enforce_cutoff = fields.Boolean(default=False)
    days = fields.Integer()
    day_type = fields.Selection([("weekday", "working days"), ("day", "days")])
    cutoff_type = fields.Selection(
        [
            ("date", "transaction date"),
            ("eom", "end of month following transaction"),
        ]
    )

    @api.multi
    def _get_new_invoice_date(self, today):
        if self.cutoff_type == "eom":
            return fields.Date.to_string(today + relativedelta(day=1))
        else:
            return fields.Date.to_string(today)

    @api.multi
    def _get_lock_date(self, date_invoice):
        for partner in self:
            if not partner.enforce_cutoff:
                continue
            today = datetime.strptime(
                fields.Date.context_today(partner), DEFAULT_SERVER_DATE_FORMAT
            )
            transaction_date = datetime.strptime(
                date_invoice, DEFAULT_SERVER_DATE_FORMAT
            )
            if transaction_date >= today:
                continue
            if partner.cutoff_type == "eom":
                if transaction_date.month >= today.month:
                    continue
                # Set to last day of month so we know if inside cutoff window
                transaction_date += relativedelta(day=31)
            if partner.days:
                weekdays = list(
                    range(5 if partner.day_type == "weekday" else 7)
                )
                transaction_date = rrule(
                    DAILY,
                    count=partner.days,
                    byweekday=weekdays,
                    dtstart=transaction_date,
                )[-1]
            if transaction_date < today:
                return partner._get_new_invoice_date(today)
        return date_invoice

    @api.model
    def _commercial_fields(self):
        """ Returns the list of fields that are managed by the commercial entity
        to which a partner belongs. These fields are meant to be hidden on
        partners that aren't `commercial entities` themselves, and will be
        delegated to the parent `commercial entity`. The list is meant to be
        extended by inheriting classes. """
        return super()._commercial_fields() + [
            'enforce_cutoff', 'days', 'day_type', 'cutoff_type']

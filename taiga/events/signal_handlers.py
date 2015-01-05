# Copyright (C) 2014 Andrey Antukh <niwi@niwi.be>
# Copyright (C) 2014 Jesús Espino <jespinog@gmail.com>
# Copyright (C) 2014 David Barragán <bameda@dbarragan.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.db.models import signals
from django.dispatch import receiver

from taiga.base.utils.db import get_typename_for_model_instance

from . import middleware as mw
from . import events


def on_save_any_model(sender, instance, created, **kwargs):
    # Ignore any object that can not have project_id
    content_type = get_typename_for_model_instance(instance)

    # Ignore any other events
    if content_type not in events.watched_types:
        return

    sesionid = mw.get_current_session_id()

    if created:
        events.emit_event_for_model(instance, sessionid=sesionid, type="create")
    else:
        events.emit_event_for_model(instance, sessionid=sesionid, type="change")


def on_delete_any_model(sender, instance, **kwargs):
    # Ignore any object that can not have project_id
    content_type = get_typename_for_model_instance(instance)

    # Ignore any other changes
    if content_type not in events.watched_types:
        return

    sesionid = mw.get_current_session_id()
    events.emit_event_for_model(instance, sessionid=sesionid, type="delete")

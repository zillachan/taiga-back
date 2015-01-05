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

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from . import functions


def get_typename_for_model_class(model:object, for_concrete_model=True) -> str:
    """
    Get typename for model instance.
    """
    if for_concrete_model:
        model = model._meta.concrete_model
    else:
        model = model._meta.proxy_for_model

    return "{0}.{1}".format(model._meta.app_label, model._meta.model_name)


def get_typename_for_model_instance(model_instance):
    """
    Get content type tuple from model instance.
    """
    ct = ContentType.objects.get_for_model(model_instance)
    return ".".join([ct.app_label, ct.model])


def reload_attribute(model_instance, attr_name):
    """Fetch the stored value of a model instance attribute.

    :param model_instance: Model instance.
    :param attr_name: Attribute name to fetch.
    """
    qs = type(model_instance).objects.filter(id=model_instance.id)
    return qs.values_list(attr_name, flat=True)[0]


@transaction.atomic
def save_in_bulk(instances, callback=None, precall=None, **save_options):
    """Save a list of model instances.

    :params instances: List of model instances.
    :params callback: Callback to call after each save.
    :params save_options: Additional options to use when saving each instance.
    """
    if callback is None:
        callback = functions.noop

    if precall is None:
        precall = functions.noop

    for instance in instances:
        created = False
        if instance.pk is None:
            created = True

        precall(instance)
        instance.save(**save_options)
        callback(instance, created=created)


@transaction.atomic
def update_in_bulk(instances, list_of_new_values, callback=None, precall=None):
    """Update a list of model instances.

    :params instances: List of model instances.
    :params new_values: List of dicts where each dict is the new data corresponding to the instance
    in the same index position as the dict.
    """
    if callback is None:
        callback = functions.noop

    if precall is None:
        precall = functions.noop

    for instance, new_values in zip(instances, list_of_new_values):
        for attribute, value in new_values.items():
            setattr(instance, attribute, value)
        precall(instance)
        instance.save()
        callback(instance)


@transaction.atomic
def update_in_bulk_with_ids(ids, list_of_new_values, model):
    """Update a table using a list of ids.

    :params ids: List of ids.
    :params new_values: List of dicts or duples where each dict/duple is the new data corresponding
    to the instance in the same index position as the dict.
    :param model: Model of the ids.
    """
    for id, new_values in zip(ids, list_of_new_values):
        model.objects.filter(id=id).update(**new_values)

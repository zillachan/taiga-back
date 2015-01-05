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

from rest_framework import serializers

from taiga.base.serializers import TagsField, PgArrayField, JsonField

from taiga.projects.userstories import models as us_models
from taiga.projects.tasks import models as task_models
from taiga.projects.issues import models as issue_models
from taiga.projects.milestones import models as milestone_models
from taiga.projects.history import models as history_models
from taiga.projects.wiki import models as wiki_models

from .models import Webhook


class HistoryDiffField(serializers.Field):
    def to_native(self, obj):
        return {key: {"from": value[0], "to": value[1]} for key, value in obj.items()}


class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhook


class UserSerializer(serializers.Serializer):
    pk = serializers.SerializerMethodField("get_pk")
    name = serializers.SerializerMethodField("get_name")

    def get_pk(self, obj):
        return obj.pk

    def get_name(self, obj):
        return obj.full_name


class UserStorySerializer(serializers.ModelSerializer):
    tags = TagsField(default=[], required=False)
    external_reference = PgArrayField(required=False)
    owner = UserSerializer()
    assigned_to = UserSerializer()
    watchers = UserSerializer(many=True)

    class Meta:
        model = us_models.UserStory
        exclude = ("backlog_order", "sprint_order", "kanban_order", "version")


class TaskSerializer(serializers.ModelSerializer):
    tags = TagsField(default=[], required=False)
    owner = UserSerializer()
    assigned_to = UserSerializer()
    watchers = UserSerializer(many=True)

    class Meta:
        model = task_models.Task


class IssueSerializer(serializers.ModelSerializer):
    tags = TagsField(default=[], required=False)
    owner = UserSerializer()
    assigned_to = UserSerializer()
    watchers = UserSerializer(many=True)

    class Meta:
        model = issue_models.Issue


class WikiPageSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    last_modifier = UserSerializer()
    watchers = UserSerializer(many=True)

    class Meta:
        model = wiki_models.WikiPage
        exclude = ("watchers", "version")


class MilestoneSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

    class Meta:
        model = milestone_models.Milestone
        exclude = ("order", "watchers")


class HistoryEntrySerializer(serializers.ModelSerializer):
    diff = HistoryDiffField()
    snapshot = JsonField()
    values = JsonField()
    user = JsonField()
    delete_comment_user = JsonField()

    class Meta:
        model = history_models.HistoryEntry

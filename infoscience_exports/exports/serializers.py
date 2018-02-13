from rest_framework import serializers

from exports.models import Export


class ExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Export
        fields = ('id', 'name',)

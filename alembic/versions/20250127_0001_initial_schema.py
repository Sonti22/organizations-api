"""Initial schema with PostGIS support

Revision ID: 20250127_0001
Revises: 
Create Date: 2025-01-27 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250127_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable PostGIS extension
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    
    # Create buildings table
    op.create_table(
        'buildings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('address', sa.String(length=500), nullable=False),
        sa.Column('location', geoalchemy2.Geography(geometry_type='POINT', srid=4326), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_buildings_address', 'buildings', ['address'])
    op.create_index('idx_buildings_location', 'buildings', ['location'], postgresql_using='gist')
    
    # Create activities table
    op.create_table(
        'activities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('path', sa.String(length=255), nullable=False, unique=True),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['activities.id'], ondelete='CASCADE'),
        sa.CheckConstraint('level >= 1 AND level <= 3', name='check_activity_level'),
    )
    op.create_index('idx_activities_name', 'activities', ['name'])
    op.create_index('idx_activities_path', 'activities', ['path'])
    op.create_index('idx_activities_level', 'activities', ['level'])
    op.create_index('idx_activities_parent_id', 'activities', ['parent_id'])
    
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('phones', postgresql.ARRAY(sa.String(length=50)), nullable=False),
        sa.Column('building_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['building_id'], ['buildings.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_organizations_name', 'organizations', ['name'])
    op.create_index('idx_organizations_building_id', 'organizations', ['building_id'])
    
    # Create organization_activities junction table
    op.create_table(
        'organization_activities',
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('activity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('organization_id', 'activity_id'),
    )


def downgrade() -> None:
    op.drop_table('organization_activities')
    op.drop_table('organizations')
    op.drop_table('activities')
    op.drop_table('buildings')
    op.execute("DROP EXTENSION IF EXISTS postgis")


"""empty message

Revision ID: fc5976d3572f
Revises: 
Create Date: 2025-03-30 01:26:54.231510

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc5976d3572f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('image_url', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('category_id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=100), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('phone_number', sa.String(length=15), nullable=True),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('menu_item',
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('image_url', sa.String(length=255), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['category.category_id'], ),
    sa.PrimaryKeyConstraint('item_id')
    )
    op.create_table('order',
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('table_number', sa.Integer(), nullable=False),
    sa.Column('order_status', sa.String(length=20), nullable=True),
    sa.Column('total_price', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('order_id')
    )
    op.create_table('order_item',
    sa.Column('order_item_id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('menu_item_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['menu_item_id'], ['menu_item.item_id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['order.order_id'], ),
    sa.PrimaryKeyConstraint('order_item_id')
    )
    op.create_table('payment',
    sa.Column('payment_id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('payment_method', sa.String(length=20), nullable=False),
    sa.Column('payment_status', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.order_id'], ),
    sa.PrimaryKeyConstraint('payment_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('payment')
    op.drop_table('order_item')
    op.drop_table('order')
    op.drop_table('menu_item')
    op.drop_table('user')
    op.drop_table('category')
    # ### end Alembic commands ###

"""baseline core-models

Revision ID: 001
Revises:
Create Date: 2026-10-15

Esquema inicial del consultorio (C-02): 8 tablas (usuario, profesional,
paciente, prestacion, sillon, turno, bloqueo, horario_atencion) con sus FKs,
unicidades, checks e índices de agenda.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "paciente",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("apellido", sa.String(length=100), nullable=False),
        sa.Column("dni", sa.String(length=20), nullable=False),
        sa.Column("telefono", sa.String(length=30), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=True),
        sa.Column("obsocial", sa.String(length=100), nullable=True),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dni", "telefono", name="uq_paciente_dni_telefono"),
    )
    op.create_table(
        "prestacion",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("duracion_minutos", sa.Integer(), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False),
        sa.CheckConstraint("duracion_minutos > 0", name="ck_prestacion_duracion"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "profesional",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("apellido", sa.String(length=100), nullable=False),
        sa.Column("especialidad", sa.String(length=100), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sillon",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "bloqueo",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profesional_id", sa.Integer(), nullable=False),
        sa.Column("sillon_id", sa.Integer(), nullable=True),
        sa.Column("fecha_hora_inicio", sa.DateTime(), nullable=False),
        sa.Column("fecha_hora_fin", sa.DateTime(), nullable=False),
        sa.Column("motivo", sa.String(length=200), nullable=True),
        sa.ForeignKeyConstraint(["profesional_id"], ["profesional.id"]),
        sa.ForeignKeyConstraint(["sillon_id"], ["sillon.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_bloqueo_profesional_inicio",
        "bloqueo",
        ["profesional_id", "fecha_hora_inicio"],
        unique=False,
    )
    op.create_table(
        "horario_atencion",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profesional_id", sa.Integer(), nullable=False),
        sa.Column("dia_semana", sa.Integer(), nullable=False),
        sa.Column("hora_inicio", sa.Time(), nullable=False),
        sa.Column("hora_fin", sa.Time(), nullable=False),
        sa.CheckConstraint(
            "dia_semana >= 0 AND dia_semana <= 6",
            name="ck_horario_atencion_dia_semana",
        ),
        sa.CheckConstraint("hora_fin > hora_inicio", name="ck_horario_atencion_franja"),
        sa.ForeignKeyConstraint(["profesional_id"], ["profesional.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "profesional_id",
            "dia_semana",
            "hora_inicio",
            name="uq_horario_atencion_franja",
        ),
    )
    op.create_table(
        "usuario",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "rol",
            sa.Enum("admin", "odontologo", name="rol_usuario", native_enum=False),
            nullable=False,
        ),
        sa.Column("profesional_id", sa.Integer(), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["profesional_id"], ["profesional.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "turno",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profesional_id", sa.Integer(), nullable=False),
        sa.Column("paciente_id", sa.Integer(), nullable=False),
        sa.Column("prestacion_id", sa.Integer(), nullable=False),
        sa.Column("sillon_id", sa.Integer(), nullable=False),
        sa.Column("fecha_hora_inicio", sa.DateTime(), nullable=False),
        sa.Column("fecha_hora_fin", sa.DateTime(), nullable=False),
        sa.Column(
            "estado",
            sa.Enum(
                "reservado",
                "confirmado",
                "cancelado",
                "completado",
                name="estado_turno",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("token_cancelacion", sa.String(length=64), nullable=True),
        sa.Column("creado_por", sa.Integer(), nullable=True),
        sa.Column("cancelado_en", sa.DateTime(), nullable=True),
        sa.Column("motivo_cancelacion", sa.Text(), nullable=True),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["creado_por"], ["usuario.id"]),
        sa.ForeignKeyConstraint(["paciente_id"], ["paciente.id"]),
        sa.ForeignKeyConstraint(["prestacion_id"], ["prestacion.id"]),
        sa.ForeignKeyConstraint(["profesional_id"], ["profesional.id"]),
        sa.ForeignKeyConstraint(["sillon_id"], ["sillon.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_cancelacion"),
    )
    op.create_index(
        "ix_turno_profesional_inicio",
        "turno",
        ["profesional_id", "fecha_hora_inicio"],
        unique=False,
    )
    op.create_index(
        "ix_turno_sillon_inicio",
        "turno",
        ["sillon_id", "fecha_hora_inicio"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_turno_sillon_inicio", table_name="turno")
    op.drop_index("ix_turno_profesional_inicio", table_name="turno")
    op.drop_table("turno")
    op.drop_table("usuario")
    op.drop_table("horario_atencion")
    op.drop_index("ix_bloqueo_profesional_inicio", table_name="bloqueo")
    op.drop_table("bloqueo")
    op.drop_table("sillon")
    op.drop_table("profesional")
    op.drop_table("prestacion")
    op.drop_table("paciente")

"""Advanced database tools for backend development."""

import logging
from typing import Dict, List, Any, Optional
from enum import Enum


logger = logging.getLogger(__name__)
class DatabaseType(str, Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    DYNAMODB = "dynamodb"
    ELASTICSEARCH = "elasticsearch"


def generate_database_models(
    entity_name: str,
    fields: Dict[str, str],
    language: str = "python",
    framework: str = "sqlalchemy",
    database_type: DatabaseType = DatabaseType.POSTGRESQL
) -> str:
    """Generate database models/schemas."""
    
    if language == "python":
        if framework.lower() == "sqlalchemy":
            return _generate_sqlalchemy_model(entity_name, fields)
        elif framework.lower() == "pydantic":
            return _generate_pydantic_model(entity_name, fields)
        elif framework.lower() == "django":
            return _generate_django_model(entity_name, fields, database_type)
    
    elif language == "javascript":
        if framework.lower() == "mongoose":
            return _generate_mongoose_schema(entity_name, fields)
        elif framework.lower() == "typeorm":
            return _generate_typeorm_entity(entity_name, fields)
    
    elif language == "java":
        if framework.lower() == "jpa":
            return _generate_jpa_entity(entity_name, fields)
    
    return "Language/Framework combination not supported"


def _generate_sqlalchemy_model(entity_name: str, fields: Dict[str, str]) -> str:
    """Generate SQLAlchemy model."""
    
    code = f'''from sqlalchemy import Column, String, Integer, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class {entity_name}(Base):
    """
    {entity_name} data model.
    """
    __tablename__ = "{entity_name.lower()}s"
    
    id = Column(Integer, primary_key=True, index=True)
'''
    
    type_map = {
        "string": "String",
        "int": "Integer",
        "float": "Float",
        "bool": "Boolean",
        "datetime": "DateTime",
        "text": "String",
    }
    
    for field_name, field_type in fields.items():
        col_type = type_map.get(field_type.lower(), "String")
        code += f"    {field_name} = Column({col_type})\n"
    
    code += """    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<{{{entity_name}}}({self.id})>"
"""
    
    return code


def _generate_pydantic_model(entity_name: str, fields: Dict[str, str]) -> str:
    """Generate Pydantic model."""
    
    code = f'''from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class {entity_name}Base(BaseModel):
    """Base model for {entity_name}."""
'''
    
    type_map = {
        "string": "str",
        "int": "int",
        "float": "float",
        "bool": "bool",
        "datetime": "datetime",
        "text": "str",
    }
    
    for field_name, field_type in fields.items():
        python_type = type_map.get(field_type.lower(), "str")
        code += f"    {field_name}: {python_type}\n"
    
    code += f'''
class {entity_name}Create({entity_name}Base):
    """Create model for {entity_name}."""
    pass

class {entity_name}Update({entity_name}Base):
    """Update model for {entity_name}."""
    pass

class {entity_name}(BaseModel):
    """Response model for {entity_name}."""
    id: int
'''
    
    for field_name in fields.keys():
        code += f"    {field_name}: str\n"
    
    code += """    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
"""
    
    return code


def _generate_django_model(entity_name: str, fields: Dict[str, str], database_type: DatabaseType) -> str:
    """Generate Django model."""
    
    code = f'''from django.db import models

class {entity_name}(models.Model):
    """
    {entity_name} database model.
    """
'''
    
    type_map = {
        "string": "CharField",
        "int": "IntegerField",
        "float": "FloatField",
        "bool": "BooleanField",
        "datetime": "DateTimeField",
        "text": "TextField",
    }
    
    for field_name, field_type in fields.items():
        field_class = type_map.get(field_type.lower(), "CharField")
        if field_class == "CharField":
            code += f"    {field_name} = models.{field_class}(max_length=255)\n"
        elif field_class == "DateTimeField":
            code += f"    {field_name} = models.{field_class}(auto_now_add=True)\n"
        else:
            code += f"    {field_name} = models.{field_class}()\n"
    
    code += """    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{entity_name} - {self.id}"
"""
    
    return code


def _generate_mongoose_schema(entity_name: str, fields: Dict[str, str]) -> str:
    """Generate Mongoose schema."""
    
    code = f'''const mongoose = require('mongoose');

const {entity_name.lower()}Schema = new mongoose.Schema({{
'''
    
    type_map = {
        "string": "String",
        "int": "Number",
        "float": "Number",
        "bool": "Boolean",
        "datetime": "Date",
        "text": "String",
    }
    
    for idx, (field_name, field_type) in enumerate(fields.items()):
        schema_type = type_map.get(field_type.lower(), "String")
        code += f"    {field_name}: {{\n"
        code += f"        type: {schema_type},\n"
        code += "        required: true,\n"
        code += "    },\n"
    
    code += """    createdAt: {
        type: Date,
        default: Date.now,
    },
    updatedAt: {
        type: Date,
        default: Date.now,
    },
}}, { timestamps: true });

module.exports = mongoose.model('""" + entity_name + """', """ + entity_name.lower() + """Schema);
"""
    
    return code


def _generate_typeorm_entity(entity_name: str, fields: Dict[str, str]) -> str:
    """Generate TypeORM entity."""
    
    code = f'''import {{ Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn }} from "typeorm";

@Entity()
export class {entity_name} {{
    @PrimaryGeneratedColumn()
    id: number;
    
'''
    
    type_map = {
        "string": "String",
        "int": "Number",
        "float": "Number",
        "bool": "Boolean",
        "datetime": "Date",
        "text": "String",
    }
    
    for field_name, field_type in fields.items():
        ts_type = "string" if field_type.lower() == "string" else "number" if field_type.lower() in ["int", "float"] else "boolean"
        code += f"    @Column()\n"
        code += f"    {field_name}: {ts_type};\n"
    
    code += """    
    @CreateDateColumn()
    createdAt: Date;
    
    @UpdateDateColumn()
    updatedAt: Date;
}
"""
    
    return code


def _generate_jpa_entity(entity_name: str, fields: Dict[str, str]) -> str:
    """Generate JPA entity."""
    
    code = f'''import javax.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "{entity_name.lower()}s")
public class {entity_name} {{
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
'''
    
    type_map = {
        "string": "String",
        "int": "Integer",
        "float": "Double",
        "bool": "Boolean",
        "datetime": "LocalDateTime",
        "text": "String",
    }
    
    for field_name, field_type in fields.items():
        java_type = type_map.get(field_type.lower(), "String")
        code += f"    @Column()\n"
        code += f"    private {java_type} {field_name};\n"
    
    code += """    
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt = LocalDateTime.now();
    
    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
}
"""
    
    return code


def generate_migration(
    operation: str,
    entity_name: str,
    fields: Optional[Dict[str, str]] = None,
    language: str = "python",
    migration_tool: str = "alembic"
) -> str:
    """Generate database migration script."""
    
    if language == "python" and migration_tool == "alembic":
        return _generate_alembic_migration(operation, entity_name, fields)
    
    elif language == "javascript" and migration_tool == "knex":
        return _generate_knex_migration(operation, entity_name, fields)
    
    return "Migration tool not supported"


def _generate_alembic_migration(operation: str, entity_name: str, fields: Optional[Dict[str, str]] = None) -> str:
    """Generate Alembic migration."""
    
    if operation == "create_table":
        code = f'''\"\"\"Create {entity_name} table

Revision ID: xxxxxxx
Revises: 
Create Date: 2026-03-05

\"\"\"
from alembic import op
import sqlalchemy as sa

revision = "xxxxxxx"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        '{entity_name.lower()}s',
        sa.Column('id', sa.Integer, nullable=False),
'''
        if fields:
            for field_name, field_type in fields.items():
                type_map = {{
                    'string': 'sa.String(255)',
                    'int': 'sa.Integer',
                    'float': 'sa.Float',
                    'bool': 'sa.Boolean',
                    'datetime': 'sa.DateTime',
                    'text': 'sa.Text',
                }}
                col_type = type_map.get(field_type.lower(), 'sa.String(255)')
                code += f"        sa.Column('{field_name}', {col_type}, nullable=True),\n"
        
        code += """        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('""" + entity_name.lower() + """s')
"""
    
    elif operation == "add_column":
        code = f'''\"\"\"Add column to {entity_name}

Revision ID: xxxxxxx
Revises: yyyyyyy
Create Date: 2026-03-05

\"\"\"
from alembic import op
import sqlalchemy as sa
import logging

revision = "xxxxxxx"
down_revision = "yyyyyyy"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('{entity_name.lower()}s', sa.Column('new_column', sa.String(255)))

def downgrade() -> None:
    op.drop_column('{entity_name.lower()}s', 'new_column')
'''
    
    return code


def _generate_knex_migration(operation: str, entity_name: str, fields: Optional[Dict[str, str]] = None) -> str:
    """Generate Knex migration."""
    
    if operation == "create_table":
        code = f'''exports.up = function(knex) {{
  return knex.schema.createTable('{entity_name.lower()}s', function(table) {{
    table.increments('id').primary();
'''
        if fields:
            for field_name, field_type in fields.items():
                type_map = {{
                    'string': 'string',
                    'int': 'integer',
                    'float': 'float',
                    'bool': 'boolean',
                    'datetime': 'datetime',
                    'text': 'text',
                }}
                col_type = type_map.get(field_type.lower(), 'string')
                code += f"    table.{col_type}('{field_name}');\n"
        
        code += """    table.timestamps(true, true);
  }});
}};

exports.down = function(knex) {{
  return knex.schema.dropTable('""" + entity_name.lower() + """s');
}};
"""
    
    return code


def generate_index_strategy(
    entity_name: str,
    fields: Dict[str, str],
    access_patterns: List[str],
    database_type: DatabaseType = DatabaseType.POSTGRESQL
) -> Dict[str, Any]:
    """Generate database indexing strategy."""
    
    recommendations = {
        "indexes": [],
        "composite_indexes": [],
        "full_text_indexes": [],
        "reasoning": [],
    }
    
    # Recommend single column indexes for frequently queried fields
    for field_name in access_patterns:
        if field_name in fields:
            recommendations["indexes"].append({
                "field": field_name,
                "type": "B-Tree",
                "reason": f"Frequently queried: {field_name}"
            })
    
    # Recommend composite indexes for common queries
    if len(access_patterns) > 1:
        recommendations["composite_indexes"].append({
            "fields": access_patterns[:2],
            "reason": "Common query combination"
        })
    
    # Full-text search on text fields
    for field_name, field_type in fields.items():
        if field_type.lower() == "text" and database_type == DatabaseType.POSTGRESQL:
            recommendations["full_text_indexes"].append({
                "field": field_name,
                "type": "GIN",
                "reason": "Text search capability"
            })
    
    return recommendations

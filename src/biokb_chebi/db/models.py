"""CHEBI RDBMS model definition."""

from typing import Optional, List

from sqlalchemy import (
    BLOB,
    ForeignKey,
    Integer,
    String,
    Text,
    Date,
)
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship
import datetime
from sqlalchemy.dialects.mysql import ENUM, SMALLINT, DATE, CHAR, VARCHAR
from enum import Enum


class BaseTable(DeclarativeBase):
    """Base class db schema."""

    pass


class Compound(BaseTable):
    """Class definition for the chebi_compound table."""

    __tablename__ = "chebi_compound"
    __table_args__ = {
        "comment": "Compound",
        "mysql_charset": "utf8",
        "mysql_collate": "utf8_unicode_ci",
    }
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[Optional[str]] = mapped_column(VARCHAR(1024))
    source: Mapped[Optional[str]] = mapped_column(VARCHAR(32))

    chebi_accession: Mapped[str] = mapped_column(VARCHAR(30))
    status: Mapped[Enum] = mapped_column(ENUM("C", "D", "E", "O", "S"), index=True)
    definition: Mapped[Optional[str]] = mapped_column(VARCHAR(4000))
    star: Mapped[int] = mapped_column(SMALLINT)
    modified_on: Mapped[Optional[datetime.date]] = mapped_column(DATE)
    created_by: Mapped[Optional[str]] = mapped_column(VARCHAR(50))

    chemicalData: Mapped[List["ChemicalData"]] = relationship(back_populates="compound")
    comments: Mapped[List["Comment"]] = relationship(back_populates="compound")
    database_accessions: Mapped[List["DatabaseAccession"]] = relationship(
        back_populates="compound"
    )
    names: Mapped[List["Name"]] = relationship(back_populates="compound")
    references: Mapped[List["Reference"]] = relationship(back_populates="compound")
    structures: Mapped[List["Structure"]] = relationship(back_populates="compound")
    inchis: Mapped[List["Inchi"]] = relationship(back_populates="compound")

    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("chebi_compound.id"))


class ChemicalData(BaseTable):
    """Class definition for the chebi_chemical_data table."""

    __tablename__ = "chebi_chemical_data"
    __table_args__ = {
        "comment": "Chemical data",
        "mysql_charset": "utf8",
        "mysql_collate": "utf8_unicode_ci",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    chemical_data: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(Text)

    compound_id: Mapped[int] = mapped_column(ForeignKey("chebi_compound.id"))
    compound: Mapped[Compound] = relationship(back_populates="chemicalData")


class Comment(BaseTable):
    """Class definition for the chebi_comment table."""

    __tablename__ = "chebi_comment"
    __table_args__ = {
        "comment": "Comment",
        "mysql_charset": "utf8",
        "mysql_collate": "utf8_unicode_ci",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    text: Mapped[str] = mapped_column(Text)
    created_on: Mapped[Optional[Date]] = mapped_column(Date)
    datatype: Mapped[str] = mapped_column(String(80))
    datatype_id: Mapped[int] = mapped_column(Integer)

    compound_id: Mapped[int] = mapped_column(ForeignKey("chebi_compound.id"))
    compound: Mapped[Compound] = relationship(back_populates="comments")


class Inchi(BaseTable):
    """Class definition for the chebi_inchi table."""

    __tablename__ = "chebi_inchi"
    __table_args__ = {
        "comment": "International Chemical Identifier",
        "mysql_charset": "utf8",
        "mysql_collate": "utf8_unicode_ci",
    }

    id: Mapped[int] = mapped_column(primary_key=True)

    inchi: Mapped[str] = mapped_column(Text)

    compound_id: Mapped[int] = mapped_column(ForeignKey("chebi_compound.id"))
    compound: Mapped[Compound] = relationship(back_populates="inchis")


class DatabaseAccession(BaseTable):
    """Class definition for the chebi_database_accession table."""

    __tablename__ = "chebi_database_accession"
    __table_args__ = {
        "comment": "Database accession",
        "mysql_charset": "utf8",
        "mysql_collate": "utf8_unicode_ci",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    accession_number: Mapped[Optional[str]] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(512))
    source: Mapped[str] = mapped_column(String(512))

    compound_id: Mapped[int] = mapped_column(ForeignKey("chebi_compound.id"))
    compound: Mapped[Compound] = relationship(back_populates="database_accessions")


class Name(BaseTable):
    """Class definition for the chebi_name table."""

    __tablename__ = "chebi_name"
    __table_args__ = {
        "comment": "Name",
        "mysql_charset": "utf8",
        "mysql_collate": "utf8_unicode_ci",
    }

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[Optional[str]] = mapped_column(String(4000))
    type: Mapped[str] = mapped_column(String(512))
    source: Mapped[str] = mapped_column(String(512))
    adapted: Mapped[str] = mapped_column(CHAR)
    language: Mapped[str] = mapped_column(String(512))

    compound_id: Mapped[int] = mapped_column(ForeignKey("chebi_compound.id"))
    compound: Mapped[Compound] = relationship(back_populates="names")


class Relation(BaseTable):
    """Class definition for the chebi_relation table."""

    __tablename__ = "chebi_relation"
    __table_args__ = {
        "comment": "Relation",
        "mysql_charset": "utf8",
        "mysql_collate": "utf8_unicode_ci",
    }

    id: Mapped[int] = mapped_column(primary_key=True)

    type: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(CHAR(1))

    final_id: Mapped[int] = mapped_column(ForeignKey("chebi_compound.id"))
    init_id: Mapped[int] = mapped_column(ForeignKey("chebi_compound.id"))

    final_id_compound: Mapped[Compound] = relationship(foreign_keys=[final_id])
    init_id_compound: Mapped[Compound] = relationship(foreign_keys=[init_id])


class Reference(BaseTable):
    """Class definition for the chebi_reference table."""

    __tablename__ = "chebi_reference"
    __table_args__ = {
        "comment": "Reference",
        "mysql_charset": "utf8",
        "mysql_collate": "utf8_unicode_ci",
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    reference_id: Mapped[str] = mapped_column(VARCHAR(60))
    reference_db_name: Mapped[str] = mapped_column(VARCHAR(60))
    location_in_ref: Mapped[Optional[str]] = mapped_column(VARCHAR(90))
    reference_name: Mapped[Optional[str]] = mapped_column(VARCHAR(1024))

    compound_id: Mapped[int] = mapped_column(ForeignKey("chebi_compound.id"))
    compound: Mapped[Compound] = relationship(back_populates="references")


class Structure(BaseTable):
    """Class definition for the chebi_structure table."""

    __tablename__ = "chebi_structure"
    __table_args__ = {
        "comment": "Structure",
        "mysql_charset": "utf8",
        "mysql_collate": "utf8_unicode_ci",
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    structure: Mapped[str] = mapped_column(BLOB)
    type: Mapped[str] = mapped_column(VARCHAR(30))
    dimension: Mapped[str] = mapped_column(VARCHAR(30))
    autogen_structure: Mapped[str] = mapped_column(CHAR(1))
    default_structure: Mapped[str] = mapped_column(CHAR(1))
    compound_id: Mapped[int] = mapped_column(ForeignKey("chebi_compound.id"))
    compound: Mapped[Compound] = relationship(back_populates="structures")

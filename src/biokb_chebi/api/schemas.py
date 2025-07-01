import datetime
from typing import Optional
from unittest.mock import Base

from pydantic import BaseModel


class ChemicalDataBase(BaseModel):
    chemical_data: Optional[str]
    source: str
    type: str
    compound_id: int


class ChemicalData(ChemicalDataBase):
    chemical_data: Optional[str]
    source: str
    type: str
    compound: "CompoundBase"


class ChemicalDataSearch(BaseModel):
    chemical_data: Optional[str] = None
    source: Optional[str] = None
    type: Optional[str] = None
    compound_id: Optional[int] = None


class ChemicalDataSearchResults(BaseModel):
    count: int
    offset: int
    limit: int
    results: list[ChemicalData]


class CommentBase(BaseModel):
    text: str
    created_on: Optional[datetime.date]
    datatype: str
    datatype_id: int
    compound_id: int


class InchiBase(BaseModel):
    inchi: str
    compound_id: int


class Inchi(InchiBase):
    inchi: str
    compound: "CompoundBase"


class InchiSearch(BaseModel):
    inchi: Optional[str] = None
    compound_id: Optional[int] = None


class InchiSearchResults(BaseModel):
    count: int
    offset: int
    limit: int
    results: list[Inchi]


class DatabaseAccessionBase(BaseModel):
    accession_number: Optional[str]
    type: str
    source: str
    compound_id: int


class DatabaseAccession(DatabaseAccessionBase):
    accession_number: Optional[str]
    type: str
    source: str
    compound: "CompoundBase"


class DatabaseAccessionSearch(BaseModel):
    accession_number: Optional[str] = None
    type: Optional[str] = None
    source: Optional[str] = None
    compound_id: Optional[int] = None


class DatabaseAccessionSearchResults(BaseModel):
    count: int
    offset: int
    limit: int
    results: list[DatabaseAccession]


class NameBase(BaseModel):
    name: Optional[str]
    type: str
    source: str
    adapted: str
    language: str
    compound_id: int


class Name(NameBase):
    name: Optional[str]
    type: str
    source: str
    adapted: str
    language: str
    compound: "CompoundBase"


class NameSearch(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    source: Optional[str] = None
    adapted: Optional[str] = None
    language: Optional[str] = None
    compound_id: Optional[int] = None


class NameSearchResults(BaseModel):
    count: int
    offset: int
    limit: int
    results: list[Name]


class RelationBase(BaseModel):
    type: str
    status: str
    final_id: int
    init_id: int


class Relation(RelationBase):
    type: str
    status: str
    final_id_compound: "CompoundBase"
    init_id_compound: "CompoundBase"


class RelationSearch(BaseModel):
    type: Optional[str] = None
    status: Optional[str] = None
    final_id: Optional[int] = None
    init_id: Optional[int] = None


class RelationSearchResults(BaseModel):
    count: int
    offset: int
    limit: int
    results: list[Relation]


class ReferenceBase(BaseModel):
    reference_id: str
    reference_db_name: str
    location_in_ref: Optional[str]
    reference_name: Optional[str]
    compound_id: int


class Reference(ReferenceBase):
    reference_id: str
    reference_db_name: str
    location_in_ref: Optional[str]
    reference_name: Optional[str]
    compound: "CompoundBase"


class ReferenceSearch(BaseModel):
    reference_id: Optional[str] = None
    reference_db_name: Optional[str] = None
    location_in_ref: Optional[str] = None
    reference_name: Optional[str] = None
    compound_id: Optional[int] = None


class ReferenceSearchResults(BaseModel):
    count: int
    offset: int
    limit: int
    results: list[Reference]


class StructureBase(BaseModel):
    structure: str
    type: str
    dimension: str
    autogen_structure: str
    default_structure: str
    compound_id: int


class CompoundBase(BaseModel):
    id: int
    name: Optional[str]
    source: Optional[str]
    chebi_accession: str
    status: str
    definition: Optional[str]
    star: int
    modified_on: Optional[datetime.date]
    created_by: Optional[str]
    parent_id: Optional[int]


class Compound(CompoundBase):
    chemicalData: list["ChemicalDataBase"]
    comments: list["CommentBase"]
    database_accessions: list["DatabaseAccessionBase"]
    names: list["NameBase"]
    references: list["ReferenceBase"]
    structures: list["StructureBase"]
    inchis: list["InchiBase"]


class CompoundSearch(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    source: Optional[str] = None
    chebi_accession: Optional[str] = None
    status: Optional[str] = None
    definition: Optional[str] = None
    star: Optional[int] = None
    modified_on: Optional[datetime.date] = None
    created_by: Optional[str] = None
    parent_id: Optional[int] = None


class CompoundSearchResults(BaseModel):
    count: int
    offset: int
    limit: int
    results: list[Compound]

# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/ga4gh/tool-registry-service-schemas/develop/openapi/openapi.yaml
#   timestamp: 2022-12-20T21:01:58+00:00

from __future__ import annotations

from enum import Enum
from typing import (
    Dict,
    List,
    Optional,
    Union,
)

from pydantic import (
    BaseModel,
    Field,
)


class Checksum(BaseModel):
    checksum: str = Field(..., description="The hex-string encoded checksum for the data. ")
    type: str = Field(
        ...,
        description="The digest method used to create the checksum.\nThe value (e.g. `sha-256`) SHOULD be listed as `Hash Name String` in the https://github.com/ga4gh-discovery/ga4gh-checksum/blob/master/hash-alg.csv[GA4GH Checksum Hash Algorithm Registry].\nOther values MAY be used, as long as implementors are aware of the issues discussed in https://tools.ietf.org/html/rfc6920#section-9.4[RFC6920].\nGA4GH may provide more explicit guidance for use of non-IANA-registered algorithms in the future.",
    )


class FileType(Enum):
    TEST_FILE = "TEST_FILE"
    PRIMARY_DESCRIPTOR = "PRIMARY_DESCRIPTOR"
    SECONDARY_DESCRIPTOR = "SECONDARY_DESCRIPTOR"
    CONTAINERFILE = "CONTAINERFILE"
    OTHER = "OTHER"


class ToolFile(BaseModel):
    path: Optional[str] = Field(
        None,
        description="Relative path of the file.  A descriptor's path can be used with the GA4GH .../{type}/descriptor/{relative_path} endpoint.",
    )
    file_type: Optional[FileType] = None
    checksum: Optional[Checksum] = None


class ToolClass(BaseModel):
    id: Optional[str] = Field(None, description="The unique identifier for the class.")
    name: Optional[str] = Field(None, description="A short friendly name for the class.")
    description: Optional[str] = Field(
        None, description="A longer explanation of what this class is and what it can accomplish."
    )


class ImageType(Enum):
    Docker = "Docker"
    Singularity = "Singularity"
    Conda = "Conda"


class DescriptorType(Enum):
    CWL = "CWL"
    WDL = "WDL"
    NFL = "NFL"
    GALAXY = "GALAXY"
    SMK = "SMK"


class DescriptorTypeVersion(BaseModel):
    __root__: str = Field(
        ...,
        description="The language version for a given descriptor type. The version should correspond to the actual declared version of the descriptor. For example, tools defined in CWL could have a version of `v1.0.2` whereas WDL tools may have a version of `1.0` or `draft-2`",
    )


class DescriptorTypeWithPlain(Enum):
    CWL = "CWL"
    WDL = "WDL"
    NFL = "NFL"
    GALAXY = "GALAXY"
    SMK = "SMK"
    PLAIN_CWL = "PLAIN_CWL"
    PLAIN_WDL = "PLAIN_WDL"
    PLAIN_NFL = "PLAIN_NFL"
    PLAIN_GALAXY = "PLAIN_GALAXY"
    PLAIN_SMK = "PLAIN_SMK"


class FileWrapper(BaseModel):
    content: Optional[str] = Field(
        None, description="The content of the file itself. One of url or content is required."
    )
    checksum: Optional[List[Checksum]] = Field(
        None,
        description="A production (immutable) tool version is required to have a hashcode. Not required otherwise, but might be useful to detect changes. ",
        example=[{"checksum": "ea2a5db69bd20a42976838790bc29294df3af02b", "type": "sha1"}],
    )
    image_type: Optional[Union[ImageType, DescriptorType]] = Field(
        None, description="Optionally return additional information on the type of file this is"
    )
    url: Optional[str] = Field(
        None,
        description="Optional url to the underlying content, should include version information, and can include a git hash.  Note that this URL should resolve to the raw unwrapped content that would otherwise be available in content. One of url or content is required.",
        example={
            "descriptorfile": {
                "url": "https://raw.githubusercontent.com/ICGC-TCGA-PanCancer/pcawg_delly_workflow/ea2a5db69bd20a42976838790bc29294df3af02b/delly_docker/Delly.cwl"
            },
            "containerfile": {
                "url": "https://raw.githubusercontent.com/ICGC-TCGA-PanCancer/pcawg_delly_workflow/c83478829802b4d36374870843821abe1b625a71/delly_docker/Dockerfile"
            },
        },
    )


class Error(BaseModel):
    code: int
    message: Optional[str] = "Internal Server Error"


class ImageData(BaseModel):
    registry_host: Optional[str] = Field(
        None,
        description="A docker registry or a URL to a Singularity registry. Used along with image_name to locate a specific image.",
        example=["registry.hub.docker.com"],
    )
    image_name: Optional[str] = Field(
        None,
        description="Used in conjunction with a registry_url if provided to locate images.",
        example=["quay.io/seqware/seqware_full/1.1", "ubuntu:latest"],
    )
    size: Optional[int] = Field(None, description="Size of the container in bytes.")
    updated: Optional[str] = Field(None, description="Last time the container was updated.")
    checksum: Optional[List[Checksum]] = Field(
        None,
        description="A production (immutable) tool version is required to have a hashcode. Not required otherwise, but might be useful to detect changes.  This exposes the hashcode for specific image versions to verify that the container version pulled is actually the version that was indexed by the registry.",
        example=[{"checksum": "77af4d6b9913e693e8d0b4b294fa62ade6054e6b2f1ffb617ac955dd63fb0182", "type": "sha256"}],
    )
    image_type: Optional[ImageType] = None


class ToolVersion(BaseModel):
    author: Optional[List[str]] = Field(
        None,
        description="Contact information for the author of this version of the tool in the registry. (More complex authorship information is handled by the descriptor).",
    )
    name: Optional[str] = Field(None, description="The name of the version.")
    url: str = Field(
        ...,
        description="The URL for this tool version in this registry.",
        example="http://agora.broadinstitute.org/tools/123456/versions/1",
    )
    id: str = Field(
        ..., description="An identifier of the version of this tool for this particular tool registry.", example="v1"
    )
    is_production: Optional[bool] = Field(
        None,
        description="This version of a tool is guaranteed to not change over time (for example, a  tool built from a tag in git as opposed to a branch). A production quality tool  is required to have a checksum",
    )
    images: Optional[List[ImageData]] = Field(
        None,
        description="All known docker images (and versions/hashes) used by this tool. If the tool has to evaluate any of the docker images strings at runtime, those ones cannot be reported here.",
    )
    descriptor_type: Optional[List[DescriptorType]] = Field(
        None, description="The type (or types) of descriptors available."
    )
    descriptor_type_version: Optional[Dict[str, List[DescriptorTypeVersion]]] = Field(
        None,
        description="A map providing information about the language versions used in this tool. The keys should be the same values used in the `descriptor_type` field, and the value should be an array of all the language versions used for the given `descriptor_type`. Depending on the `descriptor_type` (e.g. CWL) multiple version values may be used in a single tool.",
        example='{\n  "WDL": ["1.0", "1.0"],\n  "CWL": ["v1.0.2"],\n  "NFL": ["DSL2"]\n}\n',
    )
    containerfile: Optional[bool] = Field(
        None,
        description="Reports if this tool has a containerfile available. (For Docker-based tools, this would indicate the presence of a Dockerfile)",
    )
    meta_version: Optional[str] = Field(
        None,
        description="The version of this tool version in the registry. Iterates when fields like the description, author, etc. are updated.",
    )
    verified: Optional[bool] = Field(
        None, description="Reports whether this tool has been verified by a specific organization or individual."
    )
    verified_source: Optional[List[str]] = Field(
        None, description="Source of metadata that can support a verified tool, such as an email or URL."
    )
    signed: Optional[bool] = Field(None, description="Reports whether this version of the tool has been signed.")
    included_apps: Optional[List[str]] = Field(
        None,
        description="An array of IDs for the applications that are stored inside this tool.",
        example=["https://bio.tools/tool/mytum.de/SNAP2/1", "https://bio.tools/bioexcel_seqqc"],
    )


class Tool(BaseModel):
    url: str = Field(
        ...,
        description="The URL for this tool in this registry.",
        example="http://agora.broadinstitute.org/tools/123456",
    )
    id: str = Field(..., description="A unique identifier of the tool, scoped to this registry.", example=123456)
    aliases: Optional[List[str]] = Field(
        None,
        description="Support for this parameter is optional for tool registries that support aliases.\nA list of strings that can be used to identify this tool which could be  straight up URLs. \nThis can be used to expose alternative ids (such as GUIDs) for a tool\nfor registries. Can be used to match tools across registries.",
    )
    organization: str = Field(..., description="The organization that published the image.")
    name: Optional[str] = Field(None, description="The name of the tool.")
    toolclass: ToolClass
    description: Optional[str] = Field(None, description="The description of the tool.")
    meta_version: Optional[str] = Field(
        None,
        description="The version of this tool in the registry. Iterates when fields like the description, author, etc. are updated.",
    )
    has_checker: Optional[bool] = Field(None, description="Whether this tool has a checker tool associated with it.")
    checker_url: Optional[str] = Field(
        None,
        description="Optional url to the checker tool that will exit successfully if this tool produced the expected result given test data.",
    )
    versions: List[ToolVersion] = Field(..., description="A list of versions for this tool.")

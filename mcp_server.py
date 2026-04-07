from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("DocumentMCP", log_level="ERROR")



docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
 "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}



@mcp.tool(
    name = "read_doc",
    description= "This tool reads the content of a document that I want read",
)
def read_doc(
    doc_name: str = Field(description="Name of the document to read")
):
    if doc_name not in docs:
        raise ValueError(f"Document '{doc_name}' not found.")

    return docs[doc_name]


@mcp.tool(
    name = "edit_doc",
    description = "Edits the document by replacing existing content or substring of content with new content."
)
def edit_doc(
    doc_id: str = Field(description="Name of the document to edit"),
    old_str: str = Field(description="The existing content or substring of content to be replaced. This is Case sensitive and needs to be exact string"),
    new_str: str = Field(description="The new content that will replace the existing content or substring of content.")
) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document '{doc_id}' not found.")

    if old_str not in docs[doc_id]:
        raise ValueError(f"The string '{old_str}' was not found in document '{doc_id}'.")

    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    return f"Document '{doc_id}' has been updated successfully."


@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())


@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]


@mcp.prompt(
    name="format",
    description="Rewrites a document in markdown format. The input document can be in any format, but the output will be in markdown.",
)
def format_doc(
    doc_id: str = Field(description="Name of the document to format")
) -> list[base.Message]:
   prompt = f"""The user has a document that they want to be reformatted in markdown. The id of the document is as follows:
<document_id>
{doc_id}
</document_id>

Add in headers, bullet points, or any other markdown formatting that would make the document easier to read while keeping the content the same. Return the entire reformatted document in markdown format.

Use the edit_document tool to edit the document with the reformatted content. The old_str parameter should be the entire original content of the document and the new_str parameter should be the entire reformatted document in markdown format. Make sure to replace all of the original content with the reformatted content when using the edit_document tool.

"""
   return [base.UserMessage(content=prompt)]



@mcp.prompt(
    name="summarize",
    description="Summarizes a document in markdown format. The input document can be in any format, but the output will be in markdown.",
)
def summarize_doc(
    doc_id: str = Field(description="Name of the document to summarize")
) -> list[base.Message]:
   prompt = f"""The user has a document that they want to be summarized in markdown. The id of the document is as follows:
<document_id>
{doc_id}
</document_id>

Provide a concise summary of the document in markdown format, highlighting the key points and main ideas. Return the entire summary in markdown format.

"""
   return [base.UserMessage(content=prompt)]



if __name__ == "__main__":
    mcp.run(transport="stdio")
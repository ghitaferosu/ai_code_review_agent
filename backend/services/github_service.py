import httpx
from anyio.streams import file
from click.core import batch
import base64

GITHUB_API_URL = "https://api.github.com"

async def get_pull_request_files(
        owner:str,
        repo:str,
        pull_number:int
):
    url = ( f"{GITHUB_API_URL}/repos/"
            f"{owner}/{repo}/pulls/{pull_number}/files")

    files=[]
    async with httpx.AsyncClient(timeout=20.0) as client:
        for page in range(1,11):
            response = await client.get(url,
                                        params={"per_page": 100, "page": page},
                                        headers={"Accept": "application/vnd.github.v3+json"})

            response.raise_for_status()
            batchh = response.json()
            files.extend(batchh)

            if len(batchh) < 100:
                break

    return [
        {
            "filename": file["filename"],
            "status":file["status"],
            "additions":file["additions"],
            "deletions":file["deletions"],
            "patch":file.get("patch")
        }
        for file in files
    ]

async def get_pull_request_head(
        owner:str,
        repo:str,
        pull_number:int
)->str:
    url = ( f"{GITHUB_API_URL}/repos/{owner}/{repo}"
            f"/pulls/{pull_number}"
            )
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(url, headers={"Accept": "application/vnd.github+json"})
        response.raise_for_status()
        data = response.json()
        return data["head"]["sha"]

async def get_file_content(
        owner:str,
        repo:str,
        filname:str,
        ref:str
)->str:
    url = (f"{GITHUB_API_URL}/repos/{owner}/{repo}"
           f"/contents/{filname}")
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            url,
            params={"ref": ref},
            headers={"Accept": "application/vnd.github+json"}
        )
        response.raise_for_status()
        data = response.json()
        if data.get("encoding")!="base64":
            raise ValueError("Unsupported file encoding")
        decoded = base64.b64decode(data["content"])
        return decoded.decode("utf-8")
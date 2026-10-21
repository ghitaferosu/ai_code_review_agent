import httpx
from anyio.streams import file
from click.core import batch

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
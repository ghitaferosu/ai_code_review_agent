from backend.services.github_service import (get_pull_request_files,get_pull_request_head,get_file_content)
from backend.services.static_analyzer import analyze_python_code

MAX_FILES=10
MAX_FILE_SIZE=100_000

async def review_pull_request(
        owner:str,
        repo:str,
        pull_number:int
)->dict:
    files = await get_pull_request_files(owner,repo,pull_number)

    python_files = [f for f in files if f["filename"].endswith(".py") and f["status"]!="removed"]

    if len(python_files)>MAX_FILES:
        raise ValueError("Too many python files")

    head_sha = await get_pull_request_head(owner,repo,pull_number)

    all_issues=[]

    analyzed_files=0

    for f in python_files:
        filename = f["filename"]

        code=await get_file_content(owner,repo,filename,head_sha)

        if len(code)>MAX_FILE_SIZE:
            raise ValueError(f"File is too large: {filename}")

        issues=analyze_python_code(code)

        for issue in issues:
            all_issues.append({"filename":filename,**issue})
        analyzed_files+=1
    return {
            "repository": f"{owner}/{repo}",
            "pull_request_number": pull_number,
            "commit_sha": head_sha,
            "analyzed_files": analyzed_files,
            "issues_count": len(all_issues),
            "issues": all_issues
        }
from backend.services.github_service import *
from backend.services.hybrid_review_service import analyze_hybrid_code
from backend.services.pr_review_service import MAX_FILES,MAX_FILE_SIZE

async def review_pull_request_hybrid(owner,repo,pull_number):
    files=await get_pull_request_files(owner, repo, pull_number)
    python_files=[file for file in files if file["filename"].endswith(".py") and file["status"]!="removed"]
    if len(python_files)>MAX_FILES:
        raise ValueError("Too many python files")

    head_sha=await get_pull_request_head(owner, repo, pull_number)

    results=[]
    total_issues=0

    for file in python_files:
        filename=file["filename"]
        code=await get_file_content(owner,repo,filename,head_sha)

        if len(code)>MAX_FILE_SIZE:
            raise ValueError("File is too large")

        analysis=analyze_hybrid_code(code)

        issues_count=analysis["static_analysis"]["issues_count"]

        total_issues=total_issues+issues_count

        results.append({
            "filename":filename,
            **analysis
        })

    return {
            "repository":f"{owner}/{repo}",
            "pull_request_number":pull_number,
            "commit_sha":head_sha,
            "analyzed_files":len(results),
            "issues_count":total_issues,
            "files":results
        }
from backend.services.static_analyzer import analyze_python_code
from backend.services.ml_service import predict

def analyze_hybrid_code(code):
    issues=analyze_python_code(code)
    issues_count=len(issues)

    ml_result=predict(code)

    #compare the 2 approaches
    static_risky=issues_count>0
    ml_risky=ml_result["prediction"]==1

    agreement=static_risky==ml_risky

    if static_risky and ml_risky:
        summary="Static analysis found potential issues and ML predicted the risky class"
    elif static_risky:
        summary="Static analysis found potential issues but ML predicted the not_risky class"
    elif ml_risky:
        summary="No issues found by current static rules but ML predicted the risky class"
    else:
        summary="No issues found by current static rules and ML predicted the not_risky class"

    return {
        "static_analysis":{
            "language":"python",
            "issues_count":issues_count,
            "issues":issues
        },
        "ml_analysis":ml_result,
        "agreement":agreement,
        "summary":summary
    }
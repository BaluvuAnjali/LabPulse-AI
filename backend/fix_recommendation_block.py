from pathlib import Path

p = Path("main.py")
text = p.read_text(encoding="utf-8")

start_marker = '    return {\n        \n    recommendation_status = ('
end_marker = '\n\n\n# ============================================================\n# UPDATE REQUEST STATUS'

start = text.find(start_marker)
end = text.find(end_marker, start)

if start == -1 or end == -1:
    raise SystemExit("Expected malformed block not found. No changes made.")

correct_block = '''    recommendation_status = (
        "RECOMMENDED"
        if recommendations
        else "VERIFICATION_PENDING"
    )

    recommendation_message = (
        "A laboratory recommendation is available. "
        "Verify its actual availability before approval."
        if recommendations
        else
        "No confirmed laboratory recommendation is available. "
        "The physical laboratory inventory and venue availability "
        "must be verified. Timetable assignments below are for "
        "review only and do not indicate free laboratories."
    )

    return {
        "success": True,
        "id": request_id,
        "recommended_lab": best_lab_name,
        "recommended_lab_id": best_lab_id,
        "recommendation_score": best_score,
        "recommendation_status": recommendation_status,
        "recommendation_message": recommendation_message,
        "recommendations": recommendations,
        "timetable_assignments_to_review": timetable_assignments_to_review,
        "notification": notification,
    }'''

text = text[:start] + correct_block + text[end:]
p.write_text(text, encoding="utf-8")
print("Fixed the malformed return block.")

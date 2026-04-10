from services.ai_service import generate_summary

text = "This is a technical report about vibration analysis and turbine monitoring. " * 40

summary = generate_summary(text)

print("\n===== AI SUMMARY =====\n")
print(summary)
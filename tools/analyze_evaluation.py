import os
import pandas as pd

INPUT_FILE = "evaluation_template.csv"
OUTPUT_FILE = "evaluation_summary.csv"


def analyze_evaluation():
    if not os.path.exists(INPUT_FILE):
        print(f"{INPUT_FILE} not found")
        return

    df = pd.read_csv(INPUT_FILE)

    # แปลงข้อมูลเป็นตัวเลข
    df["success"] = pd.to_numeric(df["success"], errors="coerce")
    df["latency_ms"] = pd.to_numeric(df["latency_ms"], errors="coerce")

    # ใช้เฉพาะแถวที่กรอกผลแล้ว
    tested_df = df.dropna(subset=["success"])

    if tested_df.empty:
        print("ยังไม่มีข้อมูลผลทดสอบ ให้กรอก success ก่อน")
        return

    total_tests = len(tested_df)
    success_count = int(tested_df["success"].sum())
    accuracy = (success_count / total_tests) * 100

    avg_latency = tested_df["latency_ms"].mean()

    print("===== Overall Evaluation =====")
    print(f"Total tested cases: {total_tests}")
    print(f"Success cases: {success_count}")
    print(f"Accuracy: {accuracy:.2f}%")

    if pd.notna(avg_latency):
        print(f"Average latency: {avg_latency:.2f} ms")
    else:
        print("Average latency: No latency data")

    print("\n===== Command Summary =====")

    summary = tested_df.groupby("command").agg(
        total_tests=("success", "count"),
        success_cases=("success", "sum"),
        average_latency_ms=("latency_ms", "mean"),
    ).reset_index()

    summary["accuracy_percent"] = (
        summary["success_cases"] / summary["total_tests"] * 100
    ).round(2)

    summary["average_latency_ms"] = summary["average_latency_ms"].round(2)

    print(summary)

    summary.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"\nCreated {OUTPUT_FILE}")


if __name__ == "__main__":
    analyze_evaluation()
import csv

OUTPUT_FILE = "evaluation_template.csv"

PARTICIPANT_COUNT = 5
REPEAT_PER_COMMAND = 20

COMMANDS = [
    {
        "command": "SCROLL_DOWN",
        "expected_result": "Page scrolls down",
    },
    {
        "command": "SCROLL_UP",
        "expected_result": "Page scrolls up",
    },
    {
        "command": "CLICK",
        "expected_result": "Mouse click is performed",
    },
    {
        "command": "CONFIRM",
        "expected_result": "Enter key is pressed",
    },
    {
        "command": "CURSOR_MOVE",
        "expected_result": "Cursor moves according to hand position",
    },
    {
        "command": "THAIJO_SEARCH",
        "expected_result": "Keyword is entered and search is submitted",
    },
]


def generate_template():
    headers = [
        "test_id",
        "participant_id",
        "command",
        "trial_no",
        "expected_result",
        "actual_result",
        "success",
        "latency_ms",
        "note",
    ]

    test_id = 1

    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(headers)

        for participant_id in range(1, PARTICIPANT_COUNT + 1):
            for item in COMMANDS:
                for trial_no in range(1, REPEAT_PER_COMMAND + 1):
                    writer.writerow([
                        test_id,
                        participant_id,
                        item["command"],
                        trial_no,
                        item["expected_result"],
                        "",
                        "",
                        "",
                        "",
                    ])

                    test_id += 1

    print(f"Created {OUTPUT_FILE}")
    print(f"Total test cases: {test_id - 1}")


if __name__ == "__main__":
    generate_template()
from .crew import BondhuAICrew


def run(inputs: dict | None = None):
    inputs = inputs or {
        "user_query": "Draft a music & video plan that matches my current mood.",
    }
    crew = BondhuAICrew().crew()
    result = crew.kickoff(inputs=inputs)
    return result


if __name__ == "__main__":
    output = run()
    print("\n=== Bondhu AI Crew Output ===")
    print(output)